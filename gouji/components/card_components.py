from typing import List
from ..constants import Suit, Rank


class Card:
    """
    扑克牌类。

    表示够级游戏中的一张扑克牌，包含花色、点数和所属牌组的ID。

    属性:
        suit (Suit): 牌的花色
        rank (Rank): 牌的点数
        deck_id (int): 所属牌组的ID（用于区分多副牌）

    方法:
        __str__(): 返回牌的字符串表示，例如"♥A"或"大王"
        get_rank_display(): 仅返回牌的点数值，用于简化显示
    """

    def __init__(self, suit: Suit, rank: Rank, deck_id: int):
        """
        初始化一张扑克牌。

        参数:
            suit (Suit): 牌的花色
            rank (Rank): 牌的点数
            deck_id (int): 所属牌组的ID
        """
        self.suit = suit
        self.rank = rank
        self.deck_id = deck_id

    def __str__(self):
        """
        返回牌的字符串表示。

        对于大小王只返回其名称，对于常规牌返回花色加点数。

        返回:
            str: 牌的字符串表示，例如"♥A"或"大王"
        """
        if self.rank in [Rank.RED_JOKER, Rank.BLACK_JOKER]:
            return self.rank.value
        return f"{self.suit.value}{self.rank.value}"

    def get_rank_display(self):
        """
        获取牌面的显示值

        返回:
            str: 便于显示的牌面值表示
        """
        if self.rank == Rank.RED_JOKER:
            return "RJ"  # 改为"RJ"代替"大王"
        elif self.rank == Rank.BLACK_JOKER:
            return "BJ"  # 改为"BJ"代替"小王"
        elif self.rank == Rank.ACE:
            return "A"
        elif self.rank == Rank.JACK:
            return "J"
        elif self.rank == Rank.QUEEN:
            return "Q"
        elif self.rank == Rank.KING:
            return "K"
        else:
            # 对于数字牌，直接返回数值的字符串
            return str(self.rank.value)

    def get_rank_display(self):
        """返回牌面上的显示值"""
        return self.rank.value  # 假设rank.value是显示值，如"A"、"10"、"大王"等


class Hand:
    """
    玩家手牌类。

    表示一个玩家持有的所有牌。

    属性:
        cards (List[Card]): 玩家持有的牌列表
        sorted (bool): 标记手牌是否已经排序
    """

    def __init__(self):
        """
        初始化一个空的手牌。
        """
        self.cards: List[Card] = []
        self.sorted: bool = False  # 添加标记表示是否已排序
