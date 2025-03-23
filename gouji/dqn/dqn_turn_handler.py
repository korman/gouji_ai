import torch.optim as optim
import torch
import numpy as np
import random
import esper
from torch.nn import functional as F
from ..interface import TurnHandlerInterface
from ..components import PlayerComponent, Hand, TeamComponent, Card
from ..utils import CardPatternChecker
from .dqn_network import DQNNetwork
from collections import deque
from .replay_buffer import ReplayBuffer
from ..constants import PLAYER_COUNT, Rank
from ..interface import PlayerAction


class DQNTurnHandler(TurnHandlerInterface):
    """
    基于DQN的AI回合处理器，实现智能AI出牌逻辑和训练
    针对只考虑牌值（不考虑花色）的卡牌游戏
    """

    def __init__(
        self,
        learning_rate=0.001,
        gamma=0.99,
        epsilon=1.0,
        epsilon_decay=0.995,
        epsilon_min=0.01,
        batch_size=64,
        update_target_every=100,
    ):
        """
        初始化DQN处理器

        参数:
            learning_rate: 学习率
            gamma: 折扣因子
            epsilon: 探索率
            epsilon_decay: 探索率衰减
            epsilon_min: 最小探索率
            batch_size: 批量大小
            update_target_every: 目标网络更新频率
        """
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.batch_size = batch_size
        self.update_target_every = update_target_every

        # 状态空间大小 (手牌编码 + 最后出牌编码 + 其他玩家状态)
        # 计算牌值范围（3-17，3到A再到2，最后是小王和大王）
        self.rank_range = 15

        # 调整归一化因子，最多可能有16张同值牌(4副牌×4张)
        self.max_cards_per_rank = 16

        # 手牌编码 + 最后出牌编码 + 其他玩家手牌数量
        self.state_size = self.rank_range * 2 + 5

        # 动作空间大小 (动作ID到实际牌组合的映射)
        self.action_size = 500  # 从200增加到500
        self.action_mapping = {}  # 动作ID -> 牌组合
        self.reverse_action_mapping = {}  # 牌组合的哈希 -> 动作ID

        # 创建模型
        self.model = DQNNetwork(self.state_size, self.action_size)
        self.target_model = DQNNetwork(self.state_size, self.action_size)
        self.target_model.load_state_dict(self.model.state_dict())

        # 优化器
        self.optimizer = optim.Adam(
            self.model.parameters(), lr=self.learning_rate)

        # 经验回放
        self.replay_buffer = ReplayBuffer(capacity=20000)

        # 训练计数器
        self.train_counter = 0

        # 最近的状态和动作
        self.last_state = None
        self.last_action = None

        # 训练模式标志
        self.training_mode = True

        # 游戏历史记录
        self.game_history = []

        # 记录当前轮的奖励
        self.episode_reward = 0

    def encode_state(self, hand_cards, last_played_cards, player_info):
        """
        将游戏状态编码为神经网络输入向量（只考虑牌值）

        参数:
            hand_cards: 当前玩家手牌
            last_played_cards: 上一手牌
            player_info: 所有玩家信息

        返回:
            numpy数组: 状态向量
        """
        state = np.zeros(self.state_size)

        # 计算手牌中每个牌值的数量
        hand_rank_counts = np.zeros(self.rank_range)
        for card in hand_cards:
            rank_index = card.rank.get_value() - 3
            hand_rank_counts[rank_index] += 1

        # 编码手牌 (前15位) - 每种牌值的数量
        state[: self.rank_range] = hand_rank_counts / self.max_cards_per_rank

        # 编码其他玩家手牌数量 (最后5位)
        for i, count in enumerate(player_info):
            if i < 5:  # 只考虑其他5个玩家
                state[2 * self.rank_range + i] = min(
                    count / 20.0, 1.0
                )  # 归一化，假设最多20张牌

        return state

    def build_action_mapping(self, hand_cards, last_played_cards):
        """
        构建动作映射，将可能的出牌组合映射到动作ID
        只考虑牌值，忽略花色

        参数:
            hand_cards: 当前手牌
            last_played_cards: 上一手牌

        返回:
            int: 有效动作的数量
        """
        self.action_mapping = {}
        self.reverse_action_mapping = {}

        # 添加PASS选项
        self.action_mapping[0] = []
        self.reverse_action_mapping["pass"] = 0

        # 获取所有可能的出牌组合
        beating_combinations = CardPatternChecker.find_all_beating_combinations(
            hand_cards, last_played_cards
        )

        # 为每个组合分配一个动作ID
        for i, combo in enumerate(beating_combinations):
            self.action_mapping[i + 1] = combo
            # 只使用牌值而忽略花色进行哈希
            combo_key = "-".join(sorted([str(c.rank.value) for c in combo]))
            self.reverse_action_mapping[combo_key] = i + 1

        return len(self.action_mapping)

    def select_action(self, state, valid_actions):
        """
        根据当前状态和探索率选择动作

        参数:
            state: 当前状态
            valid_actions: 有效动作数

        返回:
            int: 选择的动作ID
        """
        if self.training_mode and random.random() < self.epsilon:
            # 探索: 随机选择一个有效动作
            return random.randint(0, valid_actions - 1)
        else:
            # 利用: 选择Q值最高的动作
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            q_values = self.model(state_tensor).detach().numpy()[0]

            # 只考虑有效动作
            valid_q_values = q_values[:valid_actions]
            return np.argmax(valid_q_values)

    def update_model(self):
        """训练DQN模型"""
        if len(self.replay_buffer) < self.batch_size:
            return

        # 从经验回放中采样
        states, actions, rewards, next_states, dones = self.replay_buffer.sample(
            self.batch_size
        )

        # 转换为张量
        states = torch.FloatTensor(np.array(states))
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.FloatTensor(np.array(next_states))
        dones = torch.FloatTensor(dones)

        # 计算当前Q值
        current_q = self.model(states).gather(
            1, actions.unsqueeze(1)).squeeze(1)

        # 计算目标Q值
        next_q = self.target_model(next_states).detach().max(1)[0]
        target_q = rewards + (1 - dones) * self.gamma * next_q

        # 计算损失并更新模型
        loss = F.mse_loss(current_q, target_q)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # 更新目标网络
        self.train_counter += 1
        if self.train_counter % self.update_target_every == 0:
            self.target_model.load_state_dict(self.model.state_dict())

        # 衰减探索率
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def record_experience(self, state, action, reward, next_state, done):
        """
        记录经验到回放缓冲区

        参数:
            state: 当前状态
            action: 选择的动作
            reward: 获得的奖励
            next_state: 下一个状态
            done: 是否结束
        """
        self.replay_buffer.add(state, action, reward, next_state, done)
        # 累计本轮奖励
        self.episode_reward += reward

    def handle_player_turn(self, game_state, player_id, play_system):
        """
        处理AI玩家的回合

        参数:
            game_state: 游戏状态组件
            player_id: AI玩家ID
            play_system: 出牌系统的引用

        返回:
            Tuple[PlayerAction, List[Card]]: 行动类型和选择的牌
        """
        # 获取当前玩家信息
        ai_entity = play_system.get_player_entity_by_id(player_id)

        if ai_entity is None:
            print(f"DQN AI玩家 {player_id} 不存在")
            return PlayerAction.PASS, []

        player = esper.component_for_entity(ai_entity, PlayerComponent)
        hand = esper.component_for_entity(ai_entity, Hand)
        team = esper.component_for_entity(ai_entity, TeamComponent)
        last_played_cards = play_system.get_last_played_cards()

        # 获取其他玩家手牌数量
        other_players_cards = play_system.get_other_players_card_count(
            player_id)

        # 编码当前状态
        current_state = self.encode_state(
            hand.cards, last_played_cards, other_players_cards
        )

        # 构建动作映射
        valid_actions = self.build_action_mapping(
            hand.cards, last_played_cards)

        # 如果是训练模式且有上一状态，记录奖励
        if self.training_mode and self.last_state is not None:
            # 计算奖励
            reward = -0.01  # 默认小惩罚以鼓励尽快出牌

            # 每出一张牌获得小奖励
            if len(self.action_mapping.get(self.last_action, [])) > 0:
                reward += 0.05 * len(self.action_mapping[self.last_action])

            # 如果玩家已经出完牌，给予大奖励
            if player_id in game_state.players_without_cards:
                rank_position = (
                    game_state.rankings.index(player_id)
                    if player_id in game_state.rankings
                    else -1
                )
                if rank_position >= 0:
                    # 排名越高奖励越大
                    reward = 10.0 * (PLAYER_COUNT - rank_position)
                    # 如果是第一名，额外大奖励
                    if rank_position == 0:
                        reward += 20.0

            # 记录经验
            done = player_id in game_state.players_without_cards
            self.record_experience(
                self.last_state, self.last_action, reward, current_state, done
            )

            # 更新模型
            self.update_model()

        # 选择动作
        action_id = self.select_action(current_state, valid_actions)
        selected_cards = self.action_mapping[action_id]

        # 记录当前状态和动作，以便下一回合使用
        self.last_state = current_state
        self.last_action = action_id

        # 根据选择的动作返回
        if not selected_cards:  # PASS
            if play_system.get_last_effective_player_id() == player_id:
                # 如果上一次有效出牌是当前玩家，说明其他玩家都PASS了
                # 这时候可以随便出牌
                selected_cards = random.choice(hand.cards)

            return PlayerAction.PASS, []
        else:
            return PlayerAction.PLAY, selected_cards

    def save_model(self, filepath):
        """保存模型到文件"""
        torch.save(
            {
                "model_state_dict": self.model.state_dict(),
                "target_model_state_dict": self.target_model.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
                "epsilon": self.epsilon,
                "train_counter": self.train_counter,
            },
            filepath,
        )
        print(f"模型已保存到: {filepath}")

    def load_model(self, filepath):
        """从文件加载模型"""
        checkpoint = torch.load(filepath)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.target_model.load_state_dict(
            checkpoint["target_model_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        self.epsilon = checkpoint["epsilon"]
        self.train_counter = checkpoint["train_counter"]
        print(f"模型已从: {filepath} 加载")

    def set_training_mode(self, training=True):
        """设置训练模式"""
        self.training_mode = training
        if not training:
            print("DQN AI已切换到评估模式")
        else:
            print("DQN AI已切换到训练模式")

    def reset_episode(self):
        """重置回合状态"""
        self.last_state = None
        self.last_action = None
        self.episode_reward = 0
