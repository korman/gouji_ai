import esper
from typing import List, Set, Optional
from ..components import Card, Hand
from .play_system import PlaySystem
from ..utils import CardPatternChecker
from ..constants import PlayStrategy


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

    def get_available_strategies(self, player_id) -> Set[PlayStrategy]:
        """
        获取所有可用的出牌策略

        参数:
            hand_cards: 当前手牌
            previous_cards: 上家出的牌（None表示可以任意出牌）

        返回:
            所有可用策略的集合
        """
        play_system = esper.get_processor(PlaySystem)

        if play_system == None:
            raise ValueError("PlaySystem not found")

        player_entity = play_system.get_player_entity_by_id(player_id)
        if player_entity == None:
            raise ValueError("Player not found")

        hand_cards = esper.component_for_entity(player_entity, Hand)
        last_played_cards = play_system.last_played_cards

        # 所有可以压过上家的出牌组合
        all_available_cards: List[List[Card]] = CardPatternChecker.find_all_beating_combinations(
            hand_cards.cards, last_played_cards)

        available_strategies = set()

        return available_strategies
