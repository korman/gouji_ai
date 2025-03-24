import esper
import logging
from gouji.core import GoujiGame
from gouji.core import DefaultAITurnHandler
from gouji.core import HumanPlayerTurnHandler
from gouji.ai import DQNTurnHandler
from gouji.ai import DQNTrainer
from gouji.components import GameStateComponent

# if __name__ == "__main__":
#     """
#     游戏主入口点。

#     创建GoujiGame实例并启动游戏。
#     当程序作为脚本直接运行时执行此代码块。
#     """

#     game = GoujiGame()

#     # 为玩家0注册人类处理器
#     game.register_handlers_for_players([0], HumanPlayerTurnHandler)

#     # 为玩家1-5注册AI处理器
#     game.register_handlers_for_players(list(range(1, 6)), DefaultAITurnHandler)

#     # 创建6个默认AI处理器，并且注册到游戏中
#     # game.register_handlers_for_players(list(range(6)), DefaultAITurnHandler)

#     game.run()

if __name__ == "__main__":
    """
    游戏主入口点 - DQN训练模式。

    创建GoujiGame实例并使用DQN进行训练。
    """

    logging.basicConfig(
        level=logging.INFO,  # 设置日志级别，低于此级别的日志将不显示
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filename="logs/debug.log",  # 可选，如果想将日志写入文件
    )

    # 创建游戏实例
    # # 创建DQN处理器 (可以为多个玩家创建不同的DQN处理器)
    # dqn_handler0 = DQNTurnHandler()
    # dqn_handler1 = DQNTurnHandler()

    # # 为玩家0和1注册DQN处理器
    # game.register_handler_for_player(0, dqn_handler0)
    # game.register_handler_for_player(1, dqn_handler1)

    # # 为玩家2-5注册普通AI处理器
    # game.register_handlers_for_players(list(range(2, 6)), DefaultAITurnHandler)

    # 创建DQN训练器
    trainer = DQNTrainer(num_episodes=10000)

    # 开始训练
    logging.info("开始DQN训练...")
    trainer.train()

    # 训练完成后保存模型

    handlers = trainer.get_dqn_handlers()
    for player_id, handler in handlers.items():
        handler.save_model(f"models/dqn_player{player_id}_final.pt")

    # 评估模型
    logging.info("开始评估模型...")
    trainer.evaluate(num_games=100)

    # 可选：使用训练好的DQN模型再玩一局
    logging.info("\n使用训练好的模型进行一局游戏演示...")
    # 设置为评估模式
    # dqn_handler0.set_training_mode(False)
    # dqn_handler1.set_training_mode(False)
    # # 重置游戏状态
    # for _, game_state in esper.get_component(GameStateComponent):
    #     game_state.phase = "dealing"
    #     game_state.current_player_id = 0
    #     game_state.players_without_cards.clear()
    #     game_state.rankings.clear()
    # # 运行一局游戏
    # game.run()

#  使用预处理的数据训练模型

# from gouji.core import GoujiGame
# from gouji.core import DefaultAITurnHandler
# from gouji.core import HumanPlayerTurnHandler
# from gouji.core import DQNTurnHandler  # 假设您将DQNTurnHandler放在core目录

# if __name__ == "__main__":
#     game = GoujiGame()

#     # 为玩家0注册人类处理器
#     game.register_handlers_for_players([0], HumanPlayerTurnHandler)

#     # 创建DQN处理器并加载预训练模型
#     # 注意：与其他处理器不同，DQNTurnHandler需要先实例化，因为它需要加载模型
#     dqn_handler = DQNTurnHandler(model_path="path/to/your/model.pth")
#     dqn_handler.stop_training()  # 确保不在游戏模式下训练

#     # 为玩家1注册DQN处理器
#     game.register_handlers_for_players([1], lambda: dqn_handler)

#     # 为玩家2-5注册AI处理器
#     game.register_handlers_for_players(list(range(2, 6)), DefaultAITurnHandler)

#     game.run()

# 训练模式 - 使用DQNTrainer训练模型

# from gouji.core import GoujiGame
# from gouji.core import DefaultAITurnHandler
# from gouji.utils.dqn_trainer import DQNTrainer
# from gouji.core import DQNTurnHandler

# if __name__ == "__main__":
#     # 创建游戏实例
#     game = GoujiGame()

#     # 创建DQN智能体
#     dqn_agent = DQNTurnHandler(action_size=200)  # 根据您的游戏调整动作空间

#     # 创建默认AI作为对手
#     default_ai = DefaultAITurnHandler

#     # 创建训练器
#     trainer = DQNTrainer(game, dqn_agent)

#     # 开始训练 (这里面会自动处理游戏环境重置和玩家设置)
#     trainer.train(num_episodes=5000, eval_interval=100)

#     # 保存最终模型
#     dqn_agent.save_model("dqn_final_model.pth")

#     # 如果想在训练后立即测试
#     dqn_agent.stop_training()

#     # 重置游戏
#     game = GoujiGame()

#     # 注册DQN智能体给玩家0
#     game.register_handlers_for_players([0], lambda: dqn_agent)

#     # 为其他玩家注册AI处理器
#     game.register_handlers_for_players(list(range(1, 6)), DefaultAITurnHandler)

#     # 运行测试游戏
#     game.run()
