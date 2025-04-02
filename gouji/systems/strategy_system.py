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
        all_available_cards: List[List[Card]] = (
            CardPatternChecker.find_all_beating_combinations(
                hand_cards.cards, last_played_cards
            )
        )

        available_strategies = set()

        if player_id != play_system.last_effective_player_id:
            # 如果当前玩家不是上家，则可以选择 PASS
            available_strategies.add(PlayStrategy.PASS)

        if len(all_available_cards) > 0:
            available_strategies.add(PlayStrategy.PLAY_MINIMAL)

            if (
                len(CardPatternChecker.find_cards_with_count(all_available_cards, 1))
                > 0
            ):
                available_strategies.add(PlayStrategy.SPLIT_SINGLE)

            if (
                len(CardPatternChecker.find_cards_with_count(all_available_cards, 2))
                > 0
            ):
                available_strategies.add(PlayStrategy.SPLIT_PAIR)

            if (
                len(CardPatternChecker.find_cards_with_count(all_available_cards, 3))
                > 0
            ):
                available_strategies.add(PlayStrategy.SPLIT_TRIPLE)

            if (
                len(CardPatternChecker.find_cards_with_count(all_available_cards, 4))
                > 0
            ):
                available_strategies.add(PlayStrategy.SPLIT_QUAD)

            if (
                len(CardPatternChecker.find_cards_with_count(all_available_cards, 5))
                > 0
            ):
                available_strategies.add(PlayStrategy.SPLIT_PENTA)

            if (
                len(
                    CardPatternChecker.find_cards_with_count(
                        all_available_cards, 6, True
                    )
                )
                > 0
            ):
                available_strategies.add(PlayStrategy.SPLIT_MULTI)

            all_no_split_cards = (
                CardPatternChecker.find_all_beating_combinations_without_splitting(
                    hand_cards.cards, last_played_cards
                )
            )

            if len(all_no_split_cards) > 0:
                # 如果有可以压过上家的出牌组合，则不允许 PASS
                available_strategies.add(PlayStrategy.PLAY_MINIMAL_INTACT)

                if (
                    len(CardPatternChecker.find_cards_with_count(all_no_split_cards, 1))
                    > 0
                ):
                    available_strategies.add(PlayStrategy.SINGLE)

                if (
                    len(CardPatternChecker.find_cards_with_count(all_no_split_cards, 2))
                    > 0
                ):
                    available_strategies.add(PlayStrategy.PAIR)

                if (
                    len(CardPatternChecker.find_cards_with_count(all_no_split_cards, 3))
                    > 0
                ):
                    available_strategies.add(PlayStrategy.TRIPLE)

                if (
                    len(CardPatternChecker.find_cards_with_count(all_no_split_cards, 4))
                    > 0
                ):
                    available_strategies.add(PlayStrategy.QUAD)

                if (
                    len(CardPatternChecker.find_cards_with_count(all_no_split_cards, 5))
                    > 0
                ):
                    available_strategies.add(PlayStrategy.PENTA)

                if (
                    len(
                        CardPatternChecker.find_cards_with_count(
                            all_no_split_cards, 6, True
                        )
                    )
                    > 0
                ):
                    available_strategies.add(PlayStrategy.MULTI)

        if len(available_strategies) == 0:
            raise ValueError("No available strategies")

        return available_strategies

    # 写一个空的策略选择函数，根据传入的策略，返回一组牌
    def select_strategy(self, player_id: int, strategy: PlayStrategy) -> List[Card]:
        """
        根据传入的策略，返回一组牌
        """
        # TODO: 实现策略选择逻辑
        pass
