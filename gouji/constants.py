from enum import Enum, auto


class Suit(Enum):
    """
    扑克牌花色枚举。

    表示扑克牌的四种基本花色以及王牌的特殊花色。
    使用Unicode字符作为花色的图形表示。

    属性:
        HEART (str): 红桃 ♥
        DIAMOND (str): 方块 ♦
        CLUB (str): 梅花 ♣
        SPADE (str): 黑桃 ♠
        JOKER (str): 王牌 🃏
    """
    HEART = "♥"
    DIAMOND = "♦"
    CLUB = "♣"
    SPADE = "♠"
    JOKER = "🃏"  # 添加王牌花色


class Rank(Enum):
    """
    扑克牌点数枚举。

    表示扑克牌的所有可能点数，包括A到K的常规牌以及大小王。

    属性:
        ACE (str): A
        TWO (str) 到 KING (str): 2-K的常规点数
        RED_JOKER (str): 大王
        BLACK_JOKER (str): 小王
    """
    ACE = "A"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    RED_JOKER = "大王"    # 大王
    BLACK_JOKER = "小王"  # 小王

    def get_value(self):
        """
        获取牌的数值大小，用于比较牌面大小。
        够级规则中的牌大小顺序: 3-10, J, Q, K, A, 2, 小王, 大王

        返回:
            int: 牌的数值大小
        """
        value_map = {
            Rank.THREE: 3,
            Rank.FOUR: 4,
            Rank.FIVE: 5,
            Rank.SIX: 6,
            Rank.SEVEN: 7,
            Rank.EIGHT: 8,
            Rank.NINE: 9,
            Rank.TEN: 10,
            Rank.JACK: 11,
            Rank.QUEEN: 12,
            Rank.KING: 13,
            Rank.ACE: 14,
            Rank.TWO: 15,
            Rank.BLACK_JOKER: 16,
            Rank.RED_JOKER: 17
        }
        return value_map[self]

    def __lt__(self, other):
        """重载小于运算符，允许直接比较牌的大小"""
        if not isinstance(other, Rank):
            return NotImplemented
        return self.get_value() < other.get_value()


class Team(Enum):
    """队伍枚举类型"""
    A = auto()
    B = auto()

    def __str__(self):
        return self.name