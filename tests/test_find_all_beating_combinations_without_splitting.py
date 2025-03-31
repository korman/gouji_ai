from gouji.components.card_components import Card, Hand
from gouji.constants import Rank, Suit
from gouji.utils import CardPatternChecker


def test_find_all_beating_combinations_without_splitting():
    """测试不拆牌组合查找函数"""

    # 创建测试用的牌
    def create_cards(rank_value: Rank, count, suit=Suit.HEART):
        """创建指定点数和数量的牌"""
        # 修改为与项目一致的Card创建方式
        return [Card(suit, rank_value, deck_id=0) for _ in range(count)]

    # 测试用例1：原始示例 - 手牌有4 4 4 4和5 5 5，目标牌是3 3 3
    print("测试用例1: 原始示例")
    hand_cards = create_cards(Rank.FOUR, 4) + create_cards(Rank.FIVE, 3)
    target_cards = create_cards(Rank.THREE, 3)

    result = CardPatternChecker.find_all_beating_combinations_without_splitting(
        hand_cards, target_cards)

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
        hand_cards, target_cards)

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
        hand_cards, target_cards)

    print(f"手牌: {hand_cards}")
    print(f"目标牌: {target_cards}")
    print(f"不拆牌组合: {result}")
    print(f"期望结果: 1个在列表 (除了炸弹2之外，其余手牌点数都小于目标牌)")
    print()

    # 测试用例4：无目标牌
    print("测试用例4: 无目标牌")
    hand_cards = create_cards(Rank.FOUR, 3) + create_cards(Rank.FIVE, 2)

    result = CardPatternChecker.find_all_beating_combinations_without_splitting(
        hand_cards, None)

    other_result = CardPatternChecker.find_all_beating_combinations(
        hand_cards, None)

    print(f"手牌: {hand_cards}")
    print(f"目标牌: 无")
    print(f"可能的出牌组合: {result}")
    print(f"不计拆牌的组合: {other_result}")
    print(f"期望结果: 所有可能的合法出牌组合")
    print()

    # 测试用例5：多种点数的牌，有的需要拆牌，有的不需要
    print("测试用例5: 多种点数的牌，有的需要拆牌，有的不需要")
    hand_cards = create_cards(Rank.FOUR, 4) + create_cards(Rank.FIVE, 2) + \
        create_cards(Rank.SIX, 2) + create_cards(Rank.EIGHT, 2)
    target_cards = create_cards(Rank.THREE, 2)

    result = CardPatternChecker.find_all_beating_combinations_without_splitting(
        hand_cards, target_cards)

    print(f"手牌: {hand_cards}")
    print(f"目标牌: {target_cards}")
    print(f"不拆牌组合: {result}")
    print(f"期望结果: 找到三个2张的组合: 两张5，两张6，两张8 (所有正好是2张且点数大于3的牌组)")
