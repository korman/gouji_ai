from gouji.core import GoujiGame
from gouji.core import DefaultAITurnHandler
from gouji.core import HumanPlayerTurnHandler

if __name__ == "__main__":
    """
    游戏主入口点。

    创建GoujiGame实例并启动游戏。
    当程序作为脚本直接运行时执行此代码块。
    """

    game = GoujiGame()

    # 为玩家0注册人类处理器
    game.register_handlers_for_players([0], HumanPlayerTurnHandler)

    # 为玩家1-5注册AI处理器
    game.register_handlers_for_players(list(range(1, 6)), DefaultAITurnHandler)

    # 创建6个默认AI处理器，并且注册到游戏中
    # game.register_handlers_for_players(list(range(6)), DefaultAITurnHandler)

    game.run()



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