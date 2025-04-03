import logging  # 日志记录模块
from gouji.core import GoujiGame
from gouji.core import DefaultAITurnHandler
from gouji.core import HumanPlayerTurnHandler
from gouji.ai import DQNTurnHandler
from gouji.ai import DQNTrainer
from gouji.components import GameStateComponent

if __name__ == "__main__":
    """
    游戏主入口点。

    创建GoujiGame实例并启动游戏。
    当程序作为脚本直接运行时执行此代码块。
    """

    # 配置日志系统
    logging.basicConfig(
        level=logging.INFO,  # 设置日志级别为INFO，低于此级别的日志不会显示
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # 设置日志格式
        # filename="logs/debug.log",  # 将日志输出到文件
    )

    for round in range(1000):
        game = GoujiGame(f"world_{round}")

        # 为玩家0注册人类处理器
        # game.register_handlers_for_players([0], HumanPlayerTurnHandler)

        # 为玩家1-5注册AI处理器
        game.register_handlers_for_players(
            list(range(0, 6)), DefaultAITurnHandler)

        # 创建6个默认AI处理器，并且注册到游戏中
        # game.register_handlers_for_players(list(range(6)), DefaultAITurnHandler)

        game.run()
        logging.info(f"第{round}局结束！")
