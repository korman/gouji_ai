import esper  # 导入esper实体组件系统
import logging  # 导入日志模块
from gouji.components import GameStateComponent  # 导入游戏状态组件
from gouji.core import GoujiGame  # 导入够级游戏核心类
from .dqn_turn_handler import DQNTurnHandler  # 导入DQN回合处理器
from gouji.core import DefaultAITurnHandler  # 导入默认AI回合处理器
from gouji.constants import PLAYER_COUNT  # 导入玩家数量常量
from gouji.systems import DatabaseSystem  # 导入数据库系统


class DQNTrainer:
    """
    DQN训练器，用于训练和评估DQN AI
    """

    def __init__(self, num_episodes=10000):
        """
        初始化训练器

        参数:
            num_episodes (int): 训练轮数，默认为10000
        """
        self._num_episodes = num_episodes
        self._dqn_handlers = {}  # 所有DQN处理器
        self._episode_rewards = []  # 每轮奖励
        self._current_game = 0  # 当前游戏局数计数器
        self._training = False  # 训练模式标志

        # 初始化第一个玩家的DQN处理器
        for player_id in range(1):
            self._dqn_handlers[player_id] = DQNTurnHandler(player_id)
            self._dqn_handlers[player_id].set_training_mode(True)

    def register_dqn_handler(self, player_id, handler):
        """
        注册DQN处理器

        参数:
            player_id (int): 玩家ID
            handler (DQNTurnHandler): 对应玩家的DQN回合处理器
        """
        self._dqn_handlers[player_id] = handler

    def train(self):
        """
        开始训练流程，执行指定轮数的训练，并定期保存模型
        """
        logging.info(f"开始DQN训练，共{self._num_episodes}轮...")
        self._training = True

        for episode in range(self._num_episodes):
            # 重置游戏
            self._reset_game()

            # 运行一轮游戏
            episode_reward = self._run_episode()
            self._episode_rewards.append(episode_reward)

            # 每100轮输出一次进度
            if (episode + 1) % 100 == 0:
                avg_reward = sum(self._episode_rewards[-100:]) / 100
                logging.info(
                    f"轮次: {episode+1}/{self._num_episodes}, 平均奖励: {avg_reward:.2f}, 探索率: {list(self._dqn_handlers.values())[0].epsilon:.2f}"
                )

                # 保存检查点
                for player_id, handler in self._dqn_handlers.items():
                    handler.save_model(
                        f"models/dqn_player_{player_id}_ep_{episode+1}.pt"
                    )

            self._current_game += 1

        self._current_game = 0

        logging.info("训练完成")

    def _reset_game(self):
        """
        重置游戏状态，准备下一轮训练
        """
        # 获取游戏状态组件并重置
        for _, game_state in esper.get_component(GameStateComponent):
            game_state.phase = "dealing"
            game_state.current_player_id = 0
            game_state.players_without_cards.clear()
            game_state.rankings.clear()

        # 重新发牌
        # 注意：这里需要有一个发牌系统，可能需要额外实现
        # 或者调用游戏中已有的发牌逻辑

    def _run_episode(self):
        """
        运行一轮游戏，返回总奖励

        返回:
            float: 本轮游戏获得的总奖励
        """
        total_reward = 0

        # 创建游戏实例
        game = None
        if self._training:
            game = GoujiGame("training_" + str(self._current_game))
        else:
            game = GoujiGame("evaluation_" + str(self._current_game))

        # 获取数据库记录系统
        db_record_system = esper.get_processor(DatabaseSystem)

        # 开始新游戏记录
        if self._training:
            db_record_system.start_new_game("training", self._current_game)
        else:
            db_record_system.start_new_game("evaluation", self._current_game)

        # 注册玩家处理器
        game.register_handler_for_player(0, self._dqn_handlers[0])
        game.register_handlers_for_players(list(range(1, 6)), DefaultAITurnHandler)

        # 运行游戏
        game.run()

        # 获取奖励并重置DQN处理器的奖励状态
        for handler in self._dqn_handlers.values():
            total_reward = handler.episode_reward
            handler.reset_episode()

        return total_reward

    def evaluate(self, num_games=100):
        """
        评估训练好的模型

        参数:
            num_games (int): 评估的游戏局数，默认为100
        """
        logging.info(f"开始评估，共{num_games}局...")

        self._training = False

        # 将所有DQN处理器设置为评估模式
        for handler in self._dqn_handlers.values():
            handler.load_model("models/dqn_player0_final.pt")
            handler.set_training_mode(False)

        # 初始化统计变量
        win_counts = {player_id: 0 for player_id in self._dqn_handlers.keys()}
        rank_sum = {player_id: 0 for player_id in self._dqn_handlers.keys()}

        # 运行评估游戏
        for game in range(num_games):
            # 重置游戏
            self._reset_game()

            # 运行一局游戏
            self._run_episode()

            # 记录结果
            for _, game_state in esper.get_component(GameStateComponent):
                for i, player_id in enumerate(game_state.rankings):
                    if player_id in self._dqn_handlers:
                        rank_sum[player_id] += i + 1
                        if i == 0:  # 第一名
                            win_counts[player_id] += 1

            # 定期输出进度
            if (game + 1) % 10 == 0:
                logging.info(f"已评估 {game+1}/{num_games} 局")

            self._current_game += 1

        self._current_game = 0

        # 输出结果
        logging.info("\n评估结果:")
        for player_id in self._dqn_handlers.keys():
            avg_rank = rank_sum[player_id] / num_games
            win_rate = win_counts[player_id] / num_games * 100
            logging.info(
                f"玩家 {player_id}: 胜率 {win_rate:.2f}%, 平均排名 {avg_rank:.2f}"
            )

        logging.info("评估完成")

    def get_dqn_handlers(self):
        """
        获取所有DQN处理器

        返回:
            dict: 玩家ID到DQN处理器的映射字典
        """
        return self._dqn_handlers
