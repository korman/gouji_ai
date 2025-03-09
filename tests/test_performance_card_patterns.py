import random
import timeit
from typing import List

import pytest

from gouji.constants import Suit, Rank
from gouji.components import Card
from gouji.utils import CardPatternChecker


def generate_random_hand(num_cards: int = 36) -> List[Card]:
    """
    随机生成指定数量的牌组

    参数:
        num_cards: 生成的牌数量，默认36张

    返回:
        随机生成的牌组
    """
    suits = list(Suit)[:-1]  # 排除JOKER
    ranks = [r for r in Rank if r not in [Rank.RED_JOKER, Rank.BLACK_JOKER]]

    hand = []
    for _ in range(num_cards):
        # 随机选择花色和点数，并指定一个随机的牌组ID
        suit = random.choice(suits)
        rank = random.choice(ranks)
        deck_id = random.randint(1, 2)  # 随机分配到1或2号牌组
        hand.append(Card(suit, rank, deck_id))

    return hand


def test_performance_find_all_valid_plays(benchmark):
    """
    使用 pytest-benchmark 进行性能测试

    参数:
        benchmark: pytest-benchmark 提供的性能测试工具
    """
    # 生成随机手牌
    hand_cards = generate_random_hand()

    # 使用 benchmark 测试函数性能
    result = benchmark(CardPatternChecker._find_all_valid_plays, hand_cards)

    # 额外的性能断言
    assert len(result) > 0, "应该生成至少一个有效的牌组合"


def test_execution_time():
    """
    直接测试方法执行时间
    """
    hand_cards = generate_random_hand()

    # 使用 timeit 进行精确时间测量
    execution_time = timeit.timeit(
        lambda: CardPatternChecker._find_all_valid_plays(hand_cards),
        number=1000  # 执行1000次
    )

    print(f"\n测试条件：36张随机牌")
    print(f"总执行时间：{execution_time:.4f}秒")
    print(f"平均每次执行时间：{execution_time/1000:.6f}秒")

    # 性能阈值断言（可根据实际情况调整）
    assert execution_time < 1.0, "方法执行时间过长"


def test_rank_distribution():
    """
    测试随机生成牌组的点数分布
    """
    hand_cards = generate_random_hand()

    # 统计点数分布
    rank_counts = {}
    for card in hand_cards:
        rank_counts[card.rank] = rank_counts.get(card.rank, 0) + 1

    print("\n牌组分布:")
    for rank, count in rank_counts.items():
        print(f"{rank.value}: {count}张")

    # 检查点数分布是否合理
    assert len(rank_counts) > 5, "随机牌组应包含至少5种不同点数"


def detailed_performance_profile():
    """
    使用 cProfile 进行详细性能分析
    注意：这不是一个测试，仅用于手动性能分析
    """
    import cProfile
    import pstats

    hand_cards = generate_random_hand()

    profiler = cProfile.Profile()
    profiler.enable()

    # 运行目标函数
    result = CardPatternChecker._find_all_valid_plays(hand_cards)

    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumulative')
    stats.print_stats()

    print(f"\n生成的有效出牌组合数量：{len(result)}")


# 如果需要手动运行详细性能分析
if __name__ == "__main__":
    detailed_performance_profile()
