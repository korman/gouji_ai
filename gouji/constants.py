from enum import Enum, auto

PLAYER_COUNT = 6
CARDS_COUNT = 54
DECK_COUNT = 4
TOTAL_CARDS_COUNT = CARDS_COUNT * DECK_COUNT
MAX_HAND_SIZE = TOTAL_CARDS_COUNT / PLAYER_COUNT


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
    RED_JOKER = "大王"  # 大王
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
            Rank.RED_JOKER: 17,
        }
        return value_map[self]

    def __lt__(self, other):
        """重载小于运算符，允许直接比较牌的大小"""
        if not isinstance(other, Rank):
            return NotImplemented
        return self.get_value() < other.get_value()


class Team(Enum):
    """
    队伍枚举类型。

    表示游戏中的两个对战队伍。

    属性:
        A: 第一个队伍
        B: 第二个队伍
    """

    A = auto()
    B = auto()

    def __str__(self):
        """
        返回队伍的字符串表示。

        返回:
            str: 队伍名称（'A' 或 'B'）
        """
        return self.name

    def __repr__(self):
        """
        返回队伍的详细字符串表示。

        返回:
            str: 队伍的详细描述
        """
        return f"Team.{self.name}"

    def opposite(self):
        """
        获取对方队伍。

        返回:
            Team: 与当前队伍对立的队伍
        """
        return Team.B if self == Team.A else Team.A


class ScoringRules:
    """
    游戏排名积分规则

    定义了根据玩家最终排名的积分规则
    """

    RANKING_SCORES = {
        0: 2,  # 第1名 +2分
        1: 1,  # 第2名 +1分
        2: 0,  # 第3名 0分
        3: 0,  # 第4名 0分
        4: -1,  # 第5名 -1分
        5: -2,  # 第6名 -2分
    }

    @classmethod
    def get_score_by_rank(cls, rank):
        """
        根据排名获取对应的分数

        参数:
            rank (int): 玩家排名（0-based索引）

        返回:
            int: 对应的积分变化
        """
        return cls.RANKING_SCORES.get(rank, 0)


class PlayStrategy(Enum):
    # 基础策略（原有）
    PLAY_MINIMAL = "出最小值的一组牌"
    PLAY_MINIMAL_INTACT = "出最小值的一组牌（不拆牌）"
    SPLIT_PLAY = "拆牌压制"
    BOMB_PLAY = "炸弹压制"
    LONG_CHAIN_PLAY = "出5个以上的小值牌"
    BIG_JOKER_PLAY = "大王压制"
    SMALL_JOKER_PLAY = "小王压制"
    PASS = "过牌"

    SINGLE = "SINGLE"  # 单牌
    PAIR = "PAIR"  # 对子
    TRIPLE = "TRIPLE"  # 三张
    QUAD = "QUAD"  # 四张
    PENTA = "PENTA"  # 五张
    MULTI = "MULTI"  # 五张以上
    SPLIT_SINGLE = "SPLIT_SINGLE"  # 拆牌出单牌
    SPLIT_PAIR = "SPLIT_PAIR"  # 拆牌出对子
    SPLIT_TRIPLE = "SPLIT_TRIPLE"  # 拆牌出三张
    SPLIT_QUAD = "SPLIT_QUAD"  # 拆牌出四张
    SPLIT_PENTA = "SPLIT_PENTA"  # 拆牌出五张
    SPLIT_MULTI = "SPLIT_MULTI"  # 拆牌出五张以上

    # # 新增团队配合策略 ★
    # FEDERAL_SUPPORT = "联邦救援"  # 帮助联邦队友解围出牌
    # SIGNAL_PASS = "信号过牌"  # 通过特定牌型向联邦传递信号
    # TAKE_BURDEN = "扛牌担当"  # 主动承担压制对手主攻手的责任

    # # 新增特殊规则策略 ★
    # BURN_PLAY = "烧牌突击"  # 满足烧牌条件时强制拦截
    # ACE_HUNTING = "追猎无头"  # 当对手成为无头时针对性打击
    # SHIELD_MODE = "护盾模式"  # 保留关键牌防止被烧牌

    # # 新增风险控制策略 ★
    # BAIT_PLAY = "诱敌陷阱"  # 出中等强度牌引诱对手消耗大牌
    # POWER_RESERVE = "保留实力"  # 刻意保留大牌到残局阶段
    # DECOY_PLAY = "佯攻牵制"  # 制造假进攻方向分散对手火力

    # # 新增态势感知策略 ★
    # KING_CONTROL = "控场威慑"  # 通过保留大小王影响对手决策
    # PRESSURE_MAINTAIN = "持续施压"  # 维持出牌权不让对手喘息
    # ENDGAME_TRAP = "残局收割"  # 识别终局阶段启动收割模式
