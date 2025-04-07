import logging
import torch.optim as optim
import torch
import numpy as np
import random
import esper
from torch.nn import functional as F
from gouji.interface import TurnHandlerInterface
from gouji.components import PlayerComponent, Hand, TeamComponent, Card
from gouji.utils import CardPatternChecker
from .dqn_network import DQNNetwork
from .replay_buffer import ReplayBuffer
from gouji.constants import MAX_HAND_SIZE, PlayStrategy
from gouji.interface import PlayerAction
from ..ai_personality import AIPersonality, RANK_REWARDS
from gouji.systems import StrategySystem


class DQNTurnHandler(TurnHandlerInterface):
    """
    基于DQN的AI回合处理器，实现智能AI出牌逻辑和训练
    针对只考虑牌值（不考虑花色）的卡牌游戏
    """

    def __init__(
        self,
        id,
        personality=None,
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
        # 设置AI性格
        self._personality = (
            personality.value if personality else AIPersonality.BALANCED.value
        )
        logging.info(f"创建 {self._personality.name} AI")

        self._id = id

        dqn_params = self._personality.get_algorithm_params("dqn")
        self._epsilon_decay = dqn_params.get("epsilon_decay", 0.995)
        self._epsilon_min = dqn_params.get("epsilon_min", 0.01)

        self._learning_rate = learning_rate
        self._gamma = gamma
        self._epsilon = epsilon
        self._batch_size = batch_size
        self._update_target_every = update_target_every
        self._reward = 0.0

        # 已经完成的游戏数量
        self._game_count = 0

        # 状态空间大小 (手牌编码 + 最后出牌编码 + 其他玩家状态)
        # 计算牌值范围（3-17，3到A再到2，最后是小王和大王）
        self._rank_range = 15

        # 调整归一化因子，最多可能有16张同值牌(4副牌×4张)
        self._max_cards_per_rank = 16

        # 手牌编码 + 最后出牌编码 + 其他玩家手牌数量
        self._state_size = self._rank_range * 2 + 5

        # 动作空间大小 (动作ID到实际牌组合的映射)
        self._action_size = len(PlayStrategy)  # 使用PlayStrategy枚举类的长度
        self._action_mapping = {}  # 动作ID -> 策略类型
        self._reverse_action_mapping = {}  # 策略类型 -> 动作ID

        # 创建模型
        self._model = DQNNetwork(self._state_size, self._action_size)
        self._target_model = DQNNetwork(self._state_size, self._action_size)
        self._target_model.load_state_dict(self._model.state_dict())

        # 优化器
        self._optimizer = optim.Adam(self._model.parameters(), lr=self._learning_rate)

        # 经验回放
        self._replay_buffer = ReplayBuffer(capacity=20000)

        # 训练计数器
        self._train_counter = 0

        # 最近的状态和动作
        self._last_state = None
        self._last_action = None

        # 训练模式标志
        self._training_mode = True

        # 游戏历史记录
        self._game_history = []

        # 记录当前轮的奖励
        self._episode_reward = 0

        # 连续PASS次数
        self._consecutive_passes = 0
        self._action_mapping = self._initialize_action_mapping()

    def _initialize_action_mapping(self):
        """
        初始化动作映射，将 PlayStrategy 枚举中每个策略映射到唯一的动作 ID
        """
        action_mapping = {}
        for idx, strategy in enumerate(PlayStrategy):
            action_mapping[idx] = strategy  # 动作 ID -> 策略枚举项
        return action_mapping

    def encode_state(self, hand_cards, last_played_cards, player_info):
        """
        将游戏状态编码为神经网络输入向量，增强对策略特征的表示
        适应4副牌情况下可能出现的多张同值牌

        参数:
            hand_cards: 当前玩家手牌
            last_played_cards: 上一手牌
            player_info: 所有玩家信息

        返回:
            numpy数组: 状态向量
        """
        # 基础状态编码（保持原有编码方式）
        state = np.zeros(self._state_size + 12)  # 增加特征位，包含更多牌型统计

        # 计算手牌中每个牌值的数量（保持不变）
        hand_rank_counts = np.zeros(self._rank_range)
        for card in hand_cards:
            rank_index = card.rank.get_value() - 3
            hand_rank_counts[rank_index] += 1

        # 编码手牌中每个牌值的数量（保持不变）
        for i in range(self._rank_range - 2):
            state[i] = hand_rank_counts[i] / 16.0  # 4副牌×4张=16张普通牌

        # 对大小王（保持不变）
        state[self._rank_range - 2] = (
            hand_rank_counts[self._rank_range - 2] / 4.0
        )  # 小王最多4张
        state[self._rank_range - 1] = (
            hand_rank_counts[self._rank_range - 1] / 4.0
        )  # 大王最多4张

        # 编码对手出牌信息
        if last_played_cards:
            last_played_rank_counts = np.zeros(self._rank_range)
            for card in last_played_cards:
                rank_index = card.rank.get_value() - 3
                last_played_rank_counts[rank_index] += 1

            for i in range(self._rank_range):
                state[self._rank_range + i] = last_played_rank_counts[i] / 16.0

        # 编码其他玩家手牌数量（保持不变）
        for i, count in enumerate(player_info):
            if i < 5:
                state[2 * self._rank_range + i] = min(count / MAX_HAND_SIZE, 1.0)

        # === 新增策略相关特征（已考虑多张牌的情况） ===
        feature_start_index = 2 * self._rank_range + 5

        # 特征1: 手牌中各种牌型数量（单牌到多张）
        singles, pairs, triples, quads, pentas, multi_cards = self._count_card_patterns(
            hand_cards
        )
        state[feature_start_index] = singles / max(len(hand_cards), 1)  # 单牌比例
        state[feature_start_index + 1] = (
            pairs * 2 / max(len(hand_cards), 1)
        )  # 对子比例 (×2因为每个对子有2张牌)
        state[feature_start_index + 2] = (
            triples * 3 / max(len(hand_cards), 1)
        )  # 三张比例
        state[feature_start_index + 3] = quads * 4 / max(len(hand_cards), 1)  # 四张比例
        state[feature_start_index + 4] = (
            pentas * 5 / max(len(hand_cards), 1)
        )  # 五张比例
        state[feature_start_index + 5] = multi_cards / max(
            len(hand_cards), 1
        )  # 五张以上的比例

        # 特征2: 各种牌型的数量统计
        state[feature_start_index + 6] = singles / 15.0  # 假设最多15个单牌
        state[feature_start_index + 7] = pairs / 8.0  # 假设最多8个对子
        state[feature_start_index + 8] = triples / 5.0  # 假设最多5个三张
        state[feature_start_index + 9] = quads / 4.0  # 假设最多4个四张
        state[feature_start_index + 10] = pentas / 3.0  # 假设最多3个五张
        # 假设最多2个六张及以上
        state[feature_start_index + 11] = (
            sum(1 for count in hand_rank_counts if count > 5) / 2.0
        )

        return state

    # 重写父类方法
    def on_game_end(self, game_state=None, rankings=None):
        """
        游戏结束时的回调方法，用于清理状态或进行学习

        参数:
            game_state: 可选，游戏结束时的状态组件
            rankings: 可选，游戏结束时的玩家排名列表
        """
        self._game_count += 1

        if self._training_mode:
            # 记录游戏历史
            self._game_history.append((game_state, rankings))

            reward = -10.0  # 默认值

            # 计算奖励
            for rank, player_id in enumerate(game_state.rankings):
                if player_id == self._id:
                    # 根据排名查找对应奖励
                    reward = RANK_REWARDS.get(
                        rank, -10.0
                    )  # 默认值为-10，以防排名超出预期
                    break

            self._reward += reward

            # 记录经验
            self.record_experience(
                self._last_state,
                self._last_action,
                self._reward,
                np.zeros(self._state_size),
                True,
            )

            # 更新模型
            self.update_model()

    def get_action_mask(self, available_strategies):
        """
        根据当前可用策略生成动作掩码

        参数:
            available_strategies: 当前回合可用的策略列表（已包含PASS如果可用）

        返回:
            action_mask: 动作掩码数组，1表示可用，0表示不可用
        """
        # 初始化全0掩码数组
        action_mask = np.zeros(len(self._action_mapping))

        # 遍历所有可用策略，将对应的动作ID设为可用
        for strategy in available_strategies:
            for action_id, mapped_strategy in self._action_mapping.items():
                if mapped_strategy == strategy:
                    action_mask[action_id] = 1
                    break  # 找到匹配项后跳出内循环

        return action_mask

    def select_action(self, state, action_mask):
        """
        根据当前状态选择动作，考虑动作掩码。

        参数:
            state: 当前状态
            action_mask: 当前有效动作掩码
            epsilon: 探索概率

        返回:
            int: 选择的动作ID
        """
        if np.random.rand() < self._epsilon:
            # 探索：从有效动作中随机选择
            valid_actions = [i for i, valid in enumerate(action_mask) if valid == 1]

            re_value = np.random.choice(valid_actions)
            return re_value
        else:
            # 利用：选择 Q 值最高的有效动作
            q_values = self._model.predict(state)[0]

            # 使用掩码将无效动作的 Q 值设置为一个极小值
            masked_q_values = q_values + (np.array(action_mask) - 1) * 1e9

            # 返回有效动作中 Q 值最高的动作
            return np.argmax(masked_q_values)

    def update_model(self):
        """训练DQN模型"""
        if len(self._replay_buffer) < self._batch_size:
            return

        # 从经验回放中采样
        states, actions, rewards, next_states, dones = self._replay_buffer.sample(
            self._batch_size
        )

        # 转换为张量
        states = torch.FloatTensor(np.array(states))
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.FloatTensor(np.array(next_states))
        dones = torch.FloatTensor(dones)

        # 计算当前Q值
        current_q = self._model(states).gather(1, actions.unsqueeze(1)).squeeze(1)

        # 计算目标Q值
        next_q = self._target_model(next_states).detach().max(1)[0]
        target_q = rewards + (1 - dones) * self._gamma * next_q

        # 计算损失并更新模型
        loss = F.mse_loss(current_q, target_q)
        self._optimizer.zero_grad()
        loss.backward()
        self._optimizer.step()

        # 更新目标网络
        self._train_counter += 1
        if self._train_counter % self._update_target_every == 0:
            self._target_model.load_state_dict(self._model.state_dict())

        # 衰减探索率
        if self._epsilon > self._epsilon_min:
            self._epsilon = max(
                1.0
                - CardPatternChecker.calculate_armor_reduction(self._game_count, 0.01),
                self._epsilon_min,
            )

    def record_experience(self, state, strategy_id, reward, next_state, done):
        """
        记录经验到回放缓冲区

        参数:
            state: 当前状态
            strategy_id: 选择的策略ID
            reward: 获得的奖励
            next_state: 下一个状态
            done: 是否结束
        """
        self._replay_buffer.add(state, strategy_id, reward, next_state, done)
        # 累计本轮奖励
        self._episode_reward = reward

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
            logging.error(f"DQN AI玩家 {player_id} 不存在")
            return PlayerAction.PASS, []

        player = esper.component_for_entity(ai_entity, PlayerComponent)
        hand = esper.component_for_entity(ai_entity, Hand)
        team = esper.component_for_entity(ai_entity, TeamComponent)
        last_played_cards = play_system.last_played_cards

        # 获取其他玩家手牌数量
        other_players_cards = play_system.get_other_players_card_count(player_id)

        # 编码当前状态
        current_state = self.encode_state(
            hand.cards, last_played_cards, other_players_cards
        )

        strategy_system: StrategySystem = esper.get_processor(StrategySystem)
        if strategy_system is None:
            raise ValueError("StrategySystem not found")

        # 获得当前可以使用的所有策略
        available_strategies = strategy_system.get_available_strategies(player_id)

        # 构建动作映射
        valid_actions = self.get_action_mask(available_strategies)

        selected_action = self.select_action(current_state, valid_actions)

        # 如果是训练模式且有上一状态，记录奖励
        if self._training_mode and self._last_state is not None:
            # 计算奖励
            reward = 0.0  # 默认小惩罚以鼓励尽快出牌

            reward -= (
                self._personality.pass_penalty * self._consecutive_passes
            )  # 连续PASS惩罚

            # 每出一张牌获得小奖励
            if len(self._action_mapping.get(self._last_action, [])) > 0:
                reward += self._personality.play_reward_factor * len(
                    self._action_mapping[self._last_action]
                )

                if last_played_cards is not None:
                    diff_with_last_play = CardPatternChecker.get_value_difference(
                        self._action_mapping[self._last_action], last_played_cards
                    )

                    if diff_with_last_play > len(
                        self._action_mapping[self._last_action]
                    ):
                        reward -= (
                            self._personality.difference_penalty * diff_with_last_play
                        )

                # 计算上一次出牌的拆牌代价并扣减相应奖励
                last_selected_cards = self._action_mapping[self._last_action]
                if last_selected_cards:  # 确保不是PASS
                    breaking_cost = CardPatternChecker.calculate_breaking_cost(
                        last_selected_cards, hand.cards
                    )
                    # 将拆牌代价转化为负奖励，乘以系数控制惩罚力度
                    reward -= breaking_cost * self._personality.breaking_cost_factor

                    # 记录高代价拆牌情况
                    if breaking_cost > 4.0:
                        logging.debug(
                            f"高代价拆牌: {breaking_cost:.2f}, 牌值: {last_selected_cards[0].rank.get_value()}"
                        )

            self._reward += reward

        # 选择动作
        selected_cards = strategy_system.select_strategy(player_id, selected_action)

        # 记录当前状态和动作，以便下一回合使用
        self._last_state = current_state
        self._last_action = selected_action

        # 根据选择的动作返回
        if not selected_cards:  # PASS
            self._consecutive_passes += 1
            if play_system.last_effective_player_id == player_id:
                # 如果上一次有效出牌是当前玩家，说明其他玩家都PASS了
                # 这时候可以随便出牌
                selected_cards = random.choice(hand.cards)
                self._consecutive_passes = 0

            return PlayerAction.PASS, []
        else:
            self._consecutive_passes = 0
            return PlayerAction.PLAY, selected_cards

    def save_model(self, filepath):
        """保存模型到文件"""
        torch.save(
            {
                "model_state_dict": self._model.state_dict(),
                "target_model_state_dict": self._target_model.state_dict(),
                "optimizer_state_dict": self._optimizer.state_dict(),
                "epsilon": self._epsilon,
                "train_counter": self._train_counter,
            },
            filepath,
        )
        logging.info(f"模型已保存到: {filepath}")

    def load_model(self, filepath):
        """从文件加载模型"""
        checkpoint = torch.load(filepath, weights_only=False)
        self._model.load_state_dict(checkpoint["model_state_dict"])
        self._target_model.load_state_dict(checkpoint["target_model_state_dict"])
        self._optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        self._epsilon = checkpoint["epsilon"]
        self._train_counter = checkpoint["train_counter"]
        logging.info(f"模型已从: {filepath} 加载")

    def _count_card_patterns(self, cards):
        """
        统计手牌中各种牌型数量，包括单牌、对子、三张、四张、五张和更多

        参数:
            cards: 手牌列表

        返回:
            Tuple: (单牌数, 对子数, 三张数, 四张数, 五张数, 六张及以上的牌数)
        """
        if not cards:
            return 0, 0, 0, 0, 0, 0

        # 按牌值分组
        rank_groups = {}
        for card in cards:
            rank = card.rank.get_value()
            if rank not in rank_groups:
                rank_groups[rank] = []
            rank_groups[rank].append(card)

        # 统计各类牌型
        singles = sum(1 for cards in rank_groups.values() if len(cards) == 1)
        pairs = sum(1 for cards in rank_groups.values() if len(cards) == 2)
        triples = sum(1 for cards in rank_groups.values() if len(cards) == 3)
        quads = sum(1 for cards in rank_groups.values() if len(cards) == 4)
        pentas = sum(1 for cards in rank_groups.values() if len(cards) == 5)

        # 统计六张及以上
        multi_cards_total = sum(
            len(cards) for cards in rank_groups.values() if len(cards) > 5
        )

        return singles, pairs, triples, quads, pentas, multi_cards_total

    def set_training_mode(self, training=True):
        """设置训练模式"""
        self._training_mode = training
        if not training:
            logging.info("DQN AI已切换到评估模式")
        else:
            logging.info("DQN AI已切换到训练模式")

    def reset_episode(self):
        """重置回合状态"""
        self._last_state = None
        self._last_action = None
        self._episode_reward = 0
        self._reward = 0.0

    @property
    def episode_reward(self):
        """获取当前回合奖励"""
        return self._episode_reward

    @property
    def epsilon(self):
        """获取当前探索率"""
        return self._epsilon
