from gouji.core import GoujiGame
from gouji.core import DefaultAITurnHandler

if __name__ == "__main__":
    """
    游戏主入口点。

    创建GoujiGame实例并启动游戏。
    当程序作为脚本直接运行时执行此代码块。
    """

    game = GoujiGame()

    # 创建6个默认AI处理器，并且注册到游戏中
    game.register_handlers_for_players(list(range(6)), DefaultAITurnHandler)

    game.run()
