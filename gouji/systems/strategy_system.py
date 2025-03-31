import esper
from typing import List, Set, Optional
from ..components import Card
from ..core import PlayStrategy


class StrategySystem(esper.Processor):
    """
    策略系统处理器，负责管理和应用游戏策略。

    继承自esper.Processor，作为ECS架构中的处理器组件。
    该系统允许玩家选择不同的策略，并在游戏中应用这些策略。

    属性:
        strategies (List[str]): 可用的策略列表
        current_strategy (str): 当前应用的策略
    """

    def __init__(self):
        """
        初始化StrategySystem实例。

        创建一个空的策略列表，并将当前策略设置为None。
        """
        pass

    def process(self):
        """
        处理器的主要执行方法，由ECS系统自动调用。

        在当前实现中，该方法没有执行任何操作。
        """
        pass

    def get_available_strategies(
        self, hand_cards: List[Card], previous_cards: Optional[List[Card]] = None
    ) -> Set[PlayStrategy]:
        """
        获取所有可用的出牌策略

        参数:
            hand_cards: 当前手牌
            previous_cards: 上家出的牌（None表示可以任意出牌）

        返回:
            所有可用策略的集合
        """
        available_strategies = set()

        return available_strategies

    def has_singles(self, hand_cards: List[Card]) -> bool:
        """
        检查手牌中是否有单张牌(不拆牌)

        参数:
            hand_cards: 当前手牌

        返回:
            如果有单张牌，返回True；否则返回False
        """
        # 将手牌按点数分组
        rank_groups = {}
        for card in hand_cards:
            if card.rank not in rank_groups:
                rank_groups[card.rank] = []
            rank_groups[card.rank].append(card)

        # 检查是否有恰好一张的点数
        for rank, cards in rank_groups.items():
            if len(cards) == 1:
                return True

        return False

    def has_pair(self, hand_cards: List[Card]) -> bool:
        """
        检查手牌中是否有两张同点数的牌(不拆牌)

        参数:
            hand_cards: 当前手牌

        返回:
            如果有对子，返回True；否则返回False
        """
        # 将手牌按点数分组
        rank_groups = {}
        for card in hand_cards:
            if card.rank not in rank_groups:
                rank_groups[card.rank] = []
            rank_groups[card.rank].append(card)

        # 检查是否有恰好两张的点数
        for rank, cards in rank_groups.items():
            if len(cards) == 2:
                return True

        return False

    def has_three_of_a_kind(self, hand_cards: List[Card]) -> bool:
        """
        检查手牌中是否有三张同点数的牌(不拆牌)

        参数:
            hand_cards: 当前手牌

        返回:
            如果有三张同点数的牌，返回True；否则返回False
        """
        # 将手牌按点数分组
        rank_groups = {}
        for card in hand_cards:
            if card.rank not in rank_groups:
                rank_groups[card.rank] = []
            rank_groups[card.rank].append(card)

        # 检查是否有恰好三张的点数
        for rank, cards in rank_groups.items():
            if len(cards) == 3:
                return True

        return False

    def has_four_of_a_kind(self, hand_cards: List[Card]) -> bool:
        """
        检查手牌中是否有四张同点数的牌(不拆牌)

        参数:
            hand_cards: 当前手牌

        返回:
            如果有四张同点数的牌，返回True；否则返回False
        """
        # 将手牌按点数分组
        rank_groups = {}
        for card in hand_cards:
            if card.rank not in rank_groups:
                rank_groups[card.rank] = []
            rank_groups[card.rank].append(card)

        # 检查是否有恰好四张的点数
        for rank, cards in rank_groups.items():
            if len(cards) == 4:
                return True

        return False

    def has_five_of_a_kind(self, hand_cards: List[Card]) -> bool:
        """
        检查手牌中是否有五张同点数的牌(不拆牌)

        参数:
            hand_cards: 当前手牌

        返回:
            如果有五张同点数的牌，返回True；否则返回False
        """
        # 将手牌按点数分组
        rank_groups = {}
        for card in hand_cards:
            if card.rank not in rank_groups:
                rank_groups[card.rank] = []
            rank_groups[card.rank].append(card)

        # 检查是否有恰好五张的点数
        for rank, cards in rank_groups.items():
            if len(cards) == 5:
                return True

        return False

    def has_x_of_a_kind(self, hand_cards: List[Card]) -> bool:
        """
        检查手牌中是否有大于五张同点数的牌(不拆牌)

        参数:
            hand_cards: 当前手牌

        返回:
            如果有大于五张同点数的牌，返回True；否则返回False
        """
        # 将手牌按点数分组
        rank_groups = {}
        for card in hand_cards:
            if card.rank not in rank_groups:
                rank_groups[card.rank] = []
            rank_groups[card.rank].append(card)

        # 检查是否有大于五张的点数
        for rank, cards in rank_groups.items():
            if len(cards) > 5:
                return True

        return False
