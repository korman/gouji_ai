import esper
from ..components import GameStateComponent


class DQNTrainer:
    """
    DQN训练器，用于训练和评估DQN AI
    """

    def __init__(self, num_episodes=10000):
        """
        初始化训练器

        参数:
            num_episodes: 训练轮数
        """
        self.num_episodes = num_episodes
        self.dqn_handlers = {}  # 所有DQN处理器
        self.episode_rewards = []  # 每轮奖励

    def register_dqn_handler(self, player_id, handler):
        """注册DQN处理器"""
        self.dqn_handlers[player_id] = handler

    def train(self):
        """开始训练流程"""
        print(f"开始DQN训练，共{self.num_episodes}轮...")

        for episode in range(self.num_episodes):
            # 重置游戏
            self._reset_game()

            # 运行一轮游戏
            episode_reward = self._run_episode()
            self.episode_rewards.append(episode_reward)

            # 每100轮输出一次进度
            if (episode + 1) % 100 == 0:
                avg_reward = sum(self.episode_rewards[-100:]) / 100
                print(
                    f"轮次: {episode+1}/{self.num_episodes}, 平均奖励: {avg_reward:.2f}, 探索率: {list(self.dqn_handlers.values())[0].epsilon:.2f}"
                )

                # 保存检查点
                for player_id, handler in self.dqn_handlers.items():
                    handler.save_model(
                        f"model_checkpoints/dqn_player_{player_id}_ep_{episode+1}.pt"
                    )

        print("训练完成")

    def _reset_game(self):
        """重置游戏状态"""
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
        """
        total_reward = 0
        game_over = False

        # 将所有DQN处理器设置为训练模式
        for handler in self.dqn_handlers.values():
            handler.set_training_mode(True)

        # 循环直到游戏结束
        while not game_over:
            # 让游戏系统处理一回合
            esper.process()  # 使用esper.process()替代self.world.process()

            # 检查游戏是否结束
            for _, game_state in esper.get_component(GameStateComponent):
                if game_state.phase == "game_over":
                    game_over = True
                    break

            # 累计奖励
            for player_id, handler in self.dqn_handlers.items():
                # 这里假设DQN处理器内部会记录奖励
                # 实际实现可能需要额外的奖励计算逻辑
                total_reward += (
                    handler.episode_reward if hasattr(handler, "episode_reward") else 0
                )

        return total_reward

    def evaluate(self, num_games=100):
        """
        评估训练好的模型

        参数:
            num_games: 评估的游戏局数
        """
        print(f"开始评估，共{num_games}局...")

        # 将所有DQN处理器设置为评估模式
        for handler in self.dqn_handlers.values():
            handler.set_training_mode(False)

        win_counts = {player_id: 0 for player_id in self.dqn_handlers.keys()}
        rank_sum = {player_id: 0 for player_id in self.dqn_handlers.keys()}

        for game in range(num_games):
            # 重置游戏
            self._reset_game()

            # 运行一局游戏
            self._run_episode()

            # 记录结果
            for _, game_state in esper.get_component(GameStateComponent):
                for i, player_id in enumerate(game_state.rankings):
                    if player_id in self.dqn_handlers:
                        rank_sum[player_id] += i + 1
                        if i == 0:  # 第一名
                            win_counts[player_id] += 1

            if (game + 1) % 10 == 0:
                print(f"已评估 {game+1}/{num_games} 局")

        # 输出结果
        print("\n评估结果:")
        for player_id in self.dqn_handlers.keys():
            avg_rank = rank_sum[player_id] / num_games
            win_rate = win_counts[player_id] / num_games * 100
            print(f"玩家 {player_id}: 胜率 {win_rate:.2f}%, 平均排名 {avg_rank:.2f}")

        print("评估完成")
