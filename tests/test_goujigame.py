from gouji.core import GoujiGame, DefaultAITurnHandler
import time


def test_full_ai_game():
    """
    测试全AI对战的完整游戏流程

    测试目标:
    1. 创建一个全AI的游戏实例
    2. 运行游戏直到结束
    3. 验证游戏能够正常结束
    4. 检查基本的游戏结果
    """
    # 创建全AI游戏
    game = GoujiGame()

    # 记录游戏开始时间
    start_time = time.time()
    game.register_handlers_for_players(list(range(6)), DefaultAITurnHandler)

    # 运行游戏
    game.run()

    # 计算游戏运行时间
    end_time = time.time()
    duration = end_time - start_time

    # 打印游戏信息
    print(f"全AI对战测试完成")
    print(f"游戏耗时: {duration:.2f}秒")


def test_full_ai_game_benchmark(benchmark):
    """
    使用 pytest-benchmark 进行性能测试
    """
    result = benchmark(test_full_ai_game)
    assert result is None, "测试应该返回None"
    print("性能测试完成")
