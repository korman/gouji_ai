import esper
import random
from typing import List
from ..components.card_components import Card
from ..constants import Suit, Rank


class DeckSystem(esper.Processor):
    """
    牌组系统处理器，负责创建和管理游戏中使用的卡牌。

    继承自esper.Processor，作为ECS架构中的处理器组件。
    该系统创建四副完整的扑克牌（每副包含52张常规牌和2张王牌），
    并提供洗牌功能。

    属性:
        deck (List[Card]): 存储所有卡牌的列表
        initialized (bool): 标记牌组是否已初始化的标志
    """

    def __init__(self):
        """
        初始化DeckSystem实例。

        创建一个空牌组并将初始化状态设置为False。
        """
        self.deck: List[Card] = []
        self.initialized = False

    def process(self):
        """
        处理器的主要执行方法，由ECS系统自动调用。

        如果牌组尚未初始化，则创建牌组并洗牌，然后将初始化状态设置为True。
        这确保牌组仅被初始化一次。
        """
        if not self.initialized:
            self.create_deck()
            self.shuffle_deck()
            self.initialized = True

    def create_deck(self):
        """
        创建完整的牌组。

        生成4副完整的扑克牌，每副包含：
        - 52张常规牌（4种花色 × 13种点数）
        - 2张王牌（大王和小王）

        总共创建216张牌，并在控制台输出创建的牌数。
        """
        # 创建4副牌 (包含大小王)
        for deck_id in range(4):
            # 常规牌
            for suit in [Suit.HEART, Suit.DIAMOND, Suit.CLUB, Suit.SPADE]:
                for rank in [r for r in Rank if r != Rank.RED_JOKER and r != Rank.BLACK_JOKER]:
                    self.deck.append(Card(suit, rank, deck_id))

            # 添加大小王
            self.deck.append(Card(Suit.JOKER, Rank.RED_JOKER, deck_id))
            self.deck.append(Card(Suit.JOKER, Rank.BLACK_JOKER, deck_id))

        print(f"创建了 {len(self.deck)} 张牌")

    def shuffle_deck(self):
        """
        对牌组进行随机洗牌。

        使用Python的random.shuffle函数打乱deck列表中牌的顺序。
        """
        random.shuffle(self.deck)
