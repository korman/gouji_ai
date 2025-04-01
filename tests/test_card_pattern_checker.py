import pytest
from gouji.constants import Suit, Rank
from gouji.components import Card
from gouji.utils import CardPatternChecker

# 辅助函数


def create_cards(rank, count, suit=Suit.HEART, deck_id=0):
    return [Card(suit, rank, deck_id) for _ in range(count)]


def test_different_count():
    """测试不同张数的牌组比较"""
    cards1 = create_cards(Rank.FIVE, 1)  # 一张5
    cards2 = create_cards(Rank.FOUR, 2)  # 两张4
    assert not CardPatternChecker.can_beat(cards2, cards1)


def test_mixed_cards():
    """测试多张不同点数的牌组"""
    mixed_cards = [Card(Suit.HEART, Rank.THREE, 0), Card(Suit.SPADE, Rank.FOUR, 0)]
    cards = create_cards(Rank.FIVE, 2)  # 两张5
    assert not CardPatternChecker.can_beat(mixed_cards, cards)


def test_higher_single():
    """测试点数更大的单牌"""
    cards1 = create_cards(Rank.SIX, 1)  # 一张6
    cards2 = create_cards(Rank.FIVE, 1)  # 一张5
    assert CardPatternChecker.can_beat(cards1, cards2)
    assert not CardPatternChecker.can_beat(cards2, cards1)


def test_same_count_higher_rank():
    """测试相同张数，点数更大的情况"""
    cards1 = create_cards(Rank.NINE, 3)  # 三张9
    cards2 = create_cards(Rank.EIGHT, 3)  # 三张8
    assert CardPatternChecker.can_beat(cards1, cards2)


def test_key_card_comparison():
    """测试关键牌型比较"""
    cards1 = create_cards(Rank.ACE, 2)  # 两张A
    cards2 = create_cards(Rank.KING, 2)  # 两张K
    assert CardPatternChecker.can_beat(cards1, cards2)

    cards3 = create_cards(Rank.TWO, 2)  # 两张2
    assert CardPatternChecker.can_beat(cards3, cards1)


def test_joker_comparison():
    """测试王牌比较"""
    joker_small = create_cards(Rank.BLACK_JOKER, 1)  # 小王
    joker_big = create_cards(Rank.RED_JOKER, 1)  # 大王
    two_card = create_cards(Rank.TWO, 1)  # 一张2

    assert CardPatternChecker.can_beat(joker_small, two_card)
    assert CardPatternChecker.can_beat(joker_big, joker_small)


def test_find_all_beating_combinations_empty_target():
    # 测试空目标牌时的所有可能出牌组合
    cards = [
        Card(Suit.HEART, Rank.THREE, 1),
        Card(Suit.DIAMOND, Rank.THREE, 1),
        Card(Suit.CLUB, Rank.THREE, 1),
        Card(Suit.SPADE, Rank.FOUR, 1),
        Card(Suit.HEART, Rank.FOUR, 1),
    ]

    result = CardPatternChecker.find_all_beating_combinations(cards)

    # 检查结果数量和内容
    assert len(result) == 5  # 3的组合 + 2的组合

    # 检查3的组合
    three_combinations = [
        [cards[0]],
        [cards[0], cards[1]],
        [cards[0], cards[1], cards[2]],
    ]

    # 检查4的组合
    four_combinations = [[cards[3]], [cards[3], cards[4]]]

    # 验证所有3的组合都在结果中
    for combo in three_combinations:
        assert combo in result

    # 验证所有4的组合都在结果中
    for combo in four_combinations:
        assert combo in result


def test_find_all_beating_combinations_with_target():
    # 准备手牌
    hand_cards = [
        Card(Suit.HEART, Rank.FOUR, 1),
        Card(Suit.DIAMOND, Rank.FOUR, 1),
        Card(Suit.CLUB, Rank.FIVE, 1),
        Card(Suit.SPADE, Rank.FIVE, 1),
        Card(Suit.HEART, Rank.FIVE, 1),
    ]

    # 目标牌：两张3
    target_cards = [Card(Suit.HEART, Rank.THREE, 1), Card(Suit.DIAMOND, Rank.THREE, 1)]

    result = CardPatternChecker.find_all_beating_combinations(hand_cards, target_cards)

    # 详细打印返回的组合
    print("\n返回的组合:")
    for i, combo in enumerate(result, 1):
        print(f"组合 {i}:")
        for card in combo:
            print(f"  {card.suit} {card.rank}")

    # 预期结果：4 4 和 5 5 两个组合
    expected_combinations = [
        [hand_cards[0], hand_cards[1]],  # 两张4
        [hand_cards[2], hand_cards[3]],  # 两张5
    ]

    # 验证结果
    assert len(result) == 2
    for combo in expected_combinations:
        assert combo in result


def test_find_all_beating_combinations_no_valid_combinations():
    # 测试没有可以大过目标牌的组合
    hand_cards = [Card(Rank.TWO, Suit.HEART, 1), Card(Rank.TWO, Suit.DIAMOND, 1)]

    target_cards = [Card(Rank.THREE, Suit.HEART, 1), Card(Rank.THREE, Suit.DIAMOND, 1)]

    result = CardPatternChecker.find_all_beating_combinations(hand_cards, target_cards)

    # 预期结果应该是空列表
    assert len(result) == 0


def test_find_all_beating_combinations_invalid_target():
    # 测试目标牌不是同一点数的情况
    hand_cards = [Card(Rank.FOUR, Suit.HEART, 1), Card(Rank.FOUR, Suit.DIAMOND, 1)]

    target_cards = [Card(Rank.THREE, Suit.HEART, 1), Card(Rank.FOUR, Suit.DIAMOND, 1)]

    result = CardPatternChecker.find_all_beating_combinations(hand_cards, target_cards)

    # 预期结果应该是空列表
    assert len(result) == 0


def test_card_rank_comparison():
    """
    测试牌面与真实数值的大小比较
    """
    # 测试数据：包含不同特殊牌面的点数
    test_cases = [
        # 测试基本数字牌
        (Rank.THREE, 3),
        (Rank.FOUR, 4),
        (Rank.FIVE, 5),
        (Rank.SIX, 6),
        (Rank.SEVEN, 7),
        (Rank.EIGHT, 8),
        (Rank.NINE, 9),
        (Rank.TEN, 10),
        # 测试特殊牌面
        (Rank.JACK, 11),  # J
        (Rank.QUEEN, 12),  # Q
        (Rank.KING, 13),  # K
        (Rank.ACE, 14),  # A
        (Rank.TWO, 15),  # 2 (炸弹)
        # 王牌
        (Rank.BLACK_JOKER, 16),
        (Rank.RED_JOKER, 17),
    ]

    # 比较测试
    print("牌面大小比较测试：")
    for i, (rank1, value1) in enumerate(test_cases):
        for j, (rank2, value2) in enumerate(test_cases[i + 1 :], start=i + 1):
            print(f"{rank1.value}({value1}) vs {rank2.value}({value2}):")

            # 直接比较
            print(
                f"  直接比较: {rank1} {'>' if rank1.get_value() > rank2.get_value() else '<='} {rank2}"
            )

            # 验证 get_value() 方法的正确性
            assert rank1.get_value() == value1, f"{rank1} 的 get_value() 不正确"
            assert rank2.get_value() == value2, f"{rank2} 的 get_value() 不正确"

            # 打印比较结果
            comparison_result = (
                "大于" if rank1.get_value() > rank2.get_value() else "小于等于"
            )
            print(f"  {rank1.value} {comparison_result} {rank2.value}")
            print()


def test_find_all_beating_combinations_without_splitting():
    """测试不拆牌组合查找函数"""

    # 测试用例1：原始示例 - 手牌有4 4 4 4和5 5 5，目标牌是3 3 3
    print("测试用例1: 原始示例")
    hand_cards = create_cards(Rank.FOUR, 4) + create_cards(Rank.FIVE, 3)
    target_cards = create_cards(Rank.THREE, 3)

    result = CardPatternChecker.find_all_beating_combinations_without_splitting(
        hand_cards, target_cards
    )

    print(f"手牌: {hand_cards}")
    print(f"目标牌: {target_cards}")
    print(f"不拆牌组合: {result}")
    print(f"期望结果: 找到一个组合: 三张5 (因为4 4 4 4需要拆牌)")
    print()

    # 测试用例2：目标牌数量大于任何一组手牌数量
    print("测试用例2: 目标牌数量大于任何一组手牌数量")
    hand_cards = create_cards(Rank.FOUR, 2) + create_cards(Rank.FIVE, 2)
    target_cards = create_cards(Rank.THREE, 3)

    result = CardPatternChecker.find_all_beating_combinations_without_splitting(
        hand_cards, target_cards
    )

    print(f"手牌: {hand_cards}")
    print(f"目标牌: {target_cards}")
    print(f"不拆牌组合: {result}")
    print(f"期望结果: 空列表 (因为没有足够多的同点数牌)")
    print()

    # 测试用例3：手牌点数都比目标牌小
    print("测试用例3: 手牌点数都比目标牌小")
    hand_cards = create_cards(Rank.THREE, 3) + create_cards(Rank.TWO, 3)
    target_cards = create_cards(Rank.FOUR, 3)

    result = CardPatternChecker.find_all_beating_combinations_without_splitting(
        hand_cards, target_cards
    )

    print(f"手牌: {hand_cards}")
    print(f"目标牌: {target_cards}")
    print(f"不拆牌组合: {result}")
    print(f"期望结果: 1个在列表 (除了炸弹2之外，其余手牌点数都小于目标牌)")
    print()

    # 测试用例4：无目标牌
    print("测试用例4: 无目标牌")
    hand_cards = create_cards(Rank.FOUR, 3) + create_cards(Rank.FIVE, 2)

    result = CardPatternChecker.find_all_beating_combinations_without_splitting(
        hand_cards, None
    )

    other_result = CardPatternChecker.find_all_beating_combinations(hand_cards, None)

    print(f"手牌: {hand_cards}")
    print(f"目标牌: 无")
    print(f"可能的出牌组合: {result}")
    print(f"不计拆牌的组合: {other_result}")
    print(f"期望结果: 所有可能的合法出牌组合")
    print()

    # 测试用例5：多种点数的牌，有的需要拆牌，有的不需要
    print("测试用例5: 多种点数的牌，有的需要拆牌，有的不需要")
    hand_cards = (
        create_cards(Rank.FOUR, 4)
        + create_cards(Rank.FIVE, 2)
        + create_cards(Rank.SIX, 2)
        + create_cards(Rank.EIGHT, 2)
    )
    target_cards = create_cards(Rank.THREE, 2)

    result = CardPatternChecker.find_all_beating_combinations_without_splitting(
        hand_cards, target_cards
    )

    print(f"手牌: {hand_cards}")
    print(f"目标牌: {target_cards}")
    print(f"不拆牌组合: {result}")
    print(
        f"期望结果: 找到三个2张的组合: 两张5，两张6，两张8 (所有正好是2张且点数大于3的牌组)"
    )


def test_find_cards_with_count():
    """测试查找指定数量卡牌的函数"""

    # 创建测试用的牌
    def create_cards(rank_value: Rank, count, suit=Suit.HEART):
        """创建指定点数和数量的牌"""
        return [Card(suit, rank_value, deck_id=0) for _ in range(count)]

    # 构建测试数据
    cards_lists = [
        create_cards(Rank.THREE, 3),  # 三张3
        create_cards(Rank.FOUR, 3),  # 三张4
        create_cards(Rank.FIVE, 5),  # 五张5
        create_cards(Rank.SIX, 6),  # 六张6
    ]

    # 测试用例1：精确匹配 - count=3
    print("测试用例1: 精确匹配 count=3")
    result = CardPatternChecker.find_cards_with_count(cards_lists, 3)
    print(f"结果数量: {len(result)}")
    print(f"期望结果: 两组3张牌 (三张3和三张4)")
    print()

    # 测试用例2：精确匹配 - count=5
    print("测试用例2: 精确匹配 count=5")
    result = CardPatternChecker.find_cards_with_count(cards_lists, 5)
    print(f"结果数量: {len(result)}")
    print(f"期望结果: 一组5张牌 (五张5)")
    print()

    # 测试用例3：使用allow_greater=True - count=4
    print("测试用例3: 使用allow_greater=True 查找 count=4")
    result = CardPatternChecker.find_cards_with_count(
        cards_lists, 4, allow_greater=True
    )
    print(f"结果数量: {len(result)}")
    print(f"期望结果: 两组牌 (五张5和六张6)")
    print()

    # 测试用例4：使用allow_greater=True - count=3
    print("测试用例4: 使用allow_greater=True 查找 count=3")
    result = CardPatternChecker.find_cards_with_count(
        cards_lists, 3, allow_greater=True
    )
    print(f"结果数量: {len(result)}")
    print(f"期望结果: 所有四组牌 (三张3、三张4、五张5和六张6)")
    print()
