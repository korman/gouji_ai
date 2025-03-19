import esper
import numpy as np
import torch
import torch.optim as optim
import torch.nn as nn
from .replay_buffer import ReplayBuffer
from ..interface import TurnHandlerInterface
from ..components import PlayerComponent, Hand, TeamComponent, Card
from ..utils import CardPatternChecker
from ..interface import PlayerAction
from typing import List, Tuple, Dict, Any
from .poker_dqn import PokerDQN


class DQNTurnHandler(TurnHandlerInterface):
    """基于DQN的智能体回合处理器"""

    def __init__(self, state_size=None, action_size=200, hidden_size=256, model_path=None):
        """
        初始化DQN智能体

        参数:
            state_size: 状态向量大小（如未指定，将在首次调用时自动计算）
            action_size: 动作空间大小（最大可能的出牌组合数量）
            hidden_size: 神经网络隐藏层大小
            model_path: 预训练模型路径（可选）
        """
        # 基础属性
        self.action_size = action_size
        self.hidden_size = hidden_size
        self.model_path = model_path
        self.state_size = state_size
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")

        # 网络和训练相关属性（延迟初始化）
        self.policy_net = None
        self.target_net = None
        self.optimizer = None
        self.memory = ReplayBuffer(capacity=50000)

        # 训练参数
        self.gamma = 0.99  # 折扣因子
        self.epsilon = 1.0  # 探索率
        self.epsilon_min = 0.1
        self.epsilon_decay = 0.995
        self.learning_rate = 0.0001
        self.batch_size = 64
        self.update_target_every = 10

        # 训练状态
        self.train_step = 0
        self.is_training = False

        # 上一步信息（用于训练）
        self.last_state = None
        self.last_action = None
        self.last_action_idx = None
        self.last_valid_actions_mask = None

        # 游戏状态跟踪
        self.current_episode_memory = []

        # 卡牌映射（将在首次调用时初始化）
        self.card_to_idx = None
        self.idx_to_card = None
        self._initialize_card_mapping()

    def _initialize_networks(self):
        """初始化神经网络（在第一次状态计算后调用）"""
        if self.policy_net is not None:
            return  # 已经初始化

        if self.state_size is None:
            raise ValueError("无法初始化网络：状态大小未知")

        # 初始化策略网络
        self.policy_net = PokerDQN(
            self.state_size, self.action_size, self.hidden_size).to(self.device)

        # 如果提供了模型路径，加载预训练模型
        if self.model_path:
            self.policy_net.load_state_dict(torch.load(
                self.model_path, map_location=self.device))

        # 初始化目标网络
        self.target_net = PokerDQN(
            self.state_size, self.action_size, self.hidden_size).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()

        # 初始化优化器
        self.optimizer = optim.Adam(
            self.policy_net.parameters(), lr=self.learning_rate)

    def _initialize_card_mapping(self):
        """初始化卡牌到索引的映射"""
        # TODO: 根据您的卡牌实现调整此函数
        # 这里假设54张牌（52张普通牌+2张王）

        self.card_to_idx = {}
        self.idx_to_card = {}

        suits = ["SPADE", "HEART", "CLUB", "DIAMOND"]
        values = ["3", "4", "5", "6", "7", "8",
                  "9", "10", "J", "Q", "K", "A", "2"]

        # 普通牌
        idx = 0
        for suit in suits:
            for value in values:
                # TODO: 请根据您的Card类构造函数修改这里
                # self.card_to_idx[Card(suit, value)] = idx
                # self.idx_to_card[idx] = Card(suit, value)
                idx += 1

        # 王牌
        # TODO: 请根据您的Card类修改这里，添加小王和大王的映射
        # self.card_to_idx[Card("JOKER", "BLACK")] = 52
        # self.idx_to_card[52] = Card("JOKER", "BLACK")
        # self.card_to_idx[Card("JOKER", "RED")] = 53
        # self.idx_to_card[53] = Card("JOKER", "RED")

    def handle_player_turn(
        self, game_state, player_id, play_system
    ) -> Tuple[PlayerAction, List[Card]]:
        """
        处理DQN智能体的回合

        参数:
            game_state: 游戏状态组件
            player_id: AI玩家ID
            play_system: 出牌系统的引用

        返回:
            (动作类型, 出牌列表)
        """
        # 获取当前玩家实体和组件
        ai_entity = play_system.get_player_entity_by_id(player_id)

        if ai_entity is None:
            print(f"DQN玩家 {player_id} 不存在")
            return PlayerAction.PASS, []

        player = esper.component_for_entity(ai_entity, PlayerComponent)
        hand = esper.component_for_entity(ai_entity, Hand)
        team = esper.component_for_entity(ai_entity, TeamComponent)
        last_played_cards = play_system.get_last_played_cards()

        # 获取所有可能的出牌组合
        beating_combinations = CardPatternChecker.find_all_beating_combinations(
            hand.cards, last_played_cards
        )

        # 准备有效动作
        valid_actions = []
        valid_actions.append([])  # PASS动作
        valid_actions.extend(beating_combinations)

        # 创建动作掩码(0=非法,1=合法)
        valid_actions_mask = np.zeros(self.action_size)
        valid_actions_mask[0] = 1  # PASS总是合法的

        for i in range(min(len(beating_combinations), self.action_size - 1)):
            valid_actions_mask[i + 1] = 1

        # 编码当前状态
        current_state = self._encode_game_state(
            game_state, player_id, play_system)

        # 如果状态大小是第一次确定，初始化网络
        if self.state_size is None:
            self.state_size = len(current_state)
            self._initialize_networks()

        # 如果处于训练模式且有上一步状态，则存储经验
        if self.is_training and self.last_state is not None:
            # 计算奖励（需要自定义）
            reward = self._calculate_reward(game_state, player_id, play_system)

            # 判断游戏是否结束
            done = self._is_game_over(game_state)

            # 存储经验
            self.current_episode_memory.append((
                self.last_state,
                self.last_action_idx,
                reward,
                current_state,
                done,
                self.last_valid_actions_mask
            ))

            # 如果游戏结束，处理整个回合的经验
            if done:
                self._process_episode_memory()

        # 选择动作
        action_idx = self._select_action(current_state, valid_actions_mask)

        # 存储当前状态和动作（用于下一步训练）
        self.last_state = current_state
        self.last_action_idx = action_idx
        self.last_valid_actions_mask = valid_actions_mask

        # 将动作索引转换为实际卡牌
        if action_idx == 0:  # PASS
            self.last_action = []
            return PlayerAction.PASS, []
        else:
            played_cards = valid_actions[action_idx]
            self.last_action = played_cards
            return PlayerAction.PLAY, played_cards

    def _encode_game_state(self, game_state, player_id, play_system) -> np.ndarray:
        """
        将游戏状态编码为DQN输入向量

        参数:
            game_state: 游戏状态组件
            player_id: AI玩家ID
            play_system: 出牌系统的引用

        返回:
            状态向量（numpy数组）
        """
        # TODO: 实现游戏状态编码，根据您的游戏规则和组件
        # 以下是示例编码方案，您需要根据实际情况调整

        # 获取当前玩家实体和组件
        ai_entity = play_system.get_player_entity_by_id(player_id)
        player = esper.component_for_entity(ai_entity, PlayerComponent)
        hand = esper.component_for_entity(ai_entity, Hand)
        team = esper.component_for_entity(ai_entity, TeamComponent)
        last_played_cards = play_system.get_last_played_cards()

        # 1. 编码玩家手牌(独热编码，54维)
        hand_encoding = np.zeros(54)
        for card in hand.cards:
            card_idx = self._get_card_index(card)
            hand_encoding[card_idx] = 1

        # 2. 编码上一手牌(独热编码，54维)
        last_played_encoding = np.zeros(54)
        for card in last_played_cards:
            card_idx = self._get_card_index(card)
            last_played_encoding[card_idx] = 1

        # 3. 获取所有玩家信息
        all_players_info = []

        # TODO: 获取所有玩家信息，包括手牌数量、队伍等
        # 示例代码:
        for entity, (player_comp, hand_comp, team_comp) in play_system.world.get_components(PlayerComponent, Hand, TeamComponent):
            # 跳过当前玩家
            if player_comp.player_id == player_id:
                continue

            # 添加玩家信息
            player_info = [
                len(hand_comp.cards) / 20,  # 归一化手牌数量
                1 if team_comp.team == team.team else 0  # 是否是队友
            ]
            all_players_info.extend(player_info)

        # 4. 编码当前玩家在出牌顺序中的位置
        # TODO: 获取当前玩家在出牌顺序中的位置
        player_position_encoding = np.zeros(6)  # 假设最多6个玩家
        current_position = 0  # 请替换为实际位置
        player_position_encoding[current_position] = 1

        # 5. 当前阶段/局面信息
        # TODO: 添加其他有用的游戏状态信息
        game_state_info = []

        # 合并所有特征
        state_vector = np.concatenate([
            hand_encoding,
            last_played_encoding,
            np.array(all_players_info),
            player_position_encoding,
            np.array(game_state_info)
        ])

        return state_vector

    def _get_card_index(self, card) -> int:
        """
        获取卡牌的索引

        参数:
            card: 卡牌对象

        返回:
            卡牌索引(0-53)
        """
        # TODO: 根据您的卡牌实现调整此函数
        # 示例实现:
        if card in self.card_to_idx:
            return self.card_to_idx[card]
        else:
            # 如果找不到卡牌索引，返回默认值或引发错误
            print(f"警告: 无法找到卡牌 {card} 的索引")
            return 0

    def _select_action(self, state, valid_actions_mask):
        """
        选择动作(探索或利用)

        参数:
            state: 状态向量
            valid_actions_mask: 有效动作掩码

        返回:
            选择的动作索引
        """
        if not self.is_training:
            # 测试模式，直接使用最佳动作
            state_tensor = torch.FloatTensor(
                state).unsqueeze(0).to(self.device)
            with torch.no_grad():
                q_values = self.policy_net(state_tensor)

            # 应用动作掩码
            masked_q_values = q_values.cpu().numpy(
            )[0] * valid_actions_mask - 9999999 * (1 - valid_actions_mask)
            return np.argmax(masked_q_values)

        # 训练模式，使用ε-贪婪策略
        if np.random.random() < self.epsilon:
            # 探索：从有效动作中随机选择
            valid_indices = np.where(valid_actions_mask == 1)[0]
            return np.random.choice(valid_indices)
        else:
            # 利用：选择Q值最大的动作
            state_tensor = torch.FloatTensor(
                state).unsqueeze(0).to(self.device)
            with torch.no_grad():
                q_values = self.policy_net(state_tensor)

            # 应用动作掩码
            masked_q_values = q_values.cpu().numpy(
            )[0] * valid_actions_mask - 9999999 * (1 - valid_actions_mask)
            return np.argmax(masked_q_values)

    def _calculate_reward(self, game_state, player_id, play_system) -> float:
        """
        计算动作的奖励

        参数:
            game_state: 游戏状态
            player_id: 玩家ID
            play_system: 出牌系统

        返回:
            奖励值
        """
        # TODO: 实现奖励计算逻辑，根据您的游戏规则
        # 示例奖励方案:

        reward = 0.0

        # 1. 出牌减少手牌奖励
        if self.last_action:
            reward += 0.1 * len(self.last_action)  # 每出一张牌给予0.1奖励

        # 2. 出特殊牌型的奖励
        if self.last_action and len(self.last_action) > 0:
            # TODO: 检测特殊牌型（如炸弹、顺子等）并给予额外奖励
            pass

        # 3. 游戏结束奖励
        if self._is_game_over(game_state):
            # TODO: 根据游戏结果给予额外奖励/惩罚
            # 例如:
            # ai_entity = play_system.get_player_entity_by_id(player_id)
            # hand = esper.component_for_entity(ai_entity, Hand)
            # if len(hand.cards) == 0:  # 玩家出完牌
            #     reward += 10.0  # 获胜大奖励
            # else:
            #     reward -= 5.0  # 失败惩罚
            pass

        return reward

    def _is_game_over(self, game_state) -> bool:
        """
        判断游戏是否结束

        参数:
            game_state: 游戏状态

        返回:
            游戏是否结束
        """
        # TODO: 实现游戏结束判断逻辑
        # 示例实现:
        return False  # 请替换为实际游戏结束条件

    def _process_episode_memory(self):
        """处理一个完整回合的经验记忆"""
        # 如果没有经验，直接返回
        if not self.current_episode_memory:
            return

        # 将所有经验添加到回放缓冲区
        for experience in self.current_episode_memory:
            self.memory.add(*experience)

        # 清空当前回合记忆
        self.current_episode_memory = []

        # 如果缓冲区中的样本不够，暂不训练
        if len(self.memory) < self.batch_size:
            return

        # 从经验回放中采样并训练
        self._train_network()

    def _train_network(self):
        """训练DQN网络"""
        # 从经验回放中采样
        states, actions, rewards, next_states, dones, valid_actions_masks = self.memory.sample(
            self.batch_size)

        # 转移到设备
        states = states.to(self.device)
        actions = actions.to(self.device)
        rewards = rewards.to(self.device)
        next_states = next_states.to(self.device)
        dones = dones.to(self.device)
        valid_actions_masks = valid_actions_masks.to(self.device)

        # 计算当前Q值
        q_values = self.policy_net(states)
        q_values_for_actions = q_values.gather(
            1, actions.unsqueeze(1)).squeeze(1)

        # 计算目标Q值
        with torch.no_grad():
            next_q_values = self.target_net(next_states)
            # 应用有效动作掩码
            masked_next_q = next_q_values * valid_actions_masks - \
                9999999 * (1 - valid_actions_masks)
            max_next_q = masked_next_q.max(1)[0]
            target_q_values = rewards + (1 - dones) * self.gamma * max_next_q

        # 计算损失
        loss = nn.MSELoss()(q_values_for_actions, target_q_values)

        # 反向传播和优化
        self.optimizer.zero_grad()
        loss.backward()
        # 梯度裁剪
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), 1.0)
        self.optimizer.step()

        # 更新计数器和探索率
        self.train_step += 1
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

        # 定期更新目标网络
        if self.train_step % self.update_target_every == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())

    def start_training(self):
        """开始训练模式"""
        self.is_training = True
        self.train_step = 0
        self.epsilon = 1.0  # 重置探索率

    def stop_training(self):
        """停止训练模式"""
        self.is_training = False
        self.epsilon = 0.0  # 纯利用模式，不探索

    def save_model(self, path):
        """保存模型"""
        if self.policy_net is None:
            print("警告: 模型未初始化，无法保存")
            return

        torch.save(self.policy_net.state_dict(), path)
        print(f"模型已保存到: {path}")

    def load_model(self, path):
        """加载模型"""
        if self.policy_net is None:
            print("警告: 模型未初始化，无法加载")
            return

        self.policy_net.load_state_dict(
            torch.load(path, map_location=self.device))
        self.target_net.load_state_dict(self.policy_net.state_dict())
        print(f"模型已加载: {path}")
