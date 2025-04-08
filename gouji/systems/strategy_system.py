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

        if (
            player_id != play_system.last_effective_player_id
            and play_system.round_number > 1
        ):
            # 如果当前玩家不是上家，则可以选择 PASS
            available_strategies.add(PlayStrategy.PASS)

        if len(all_available_cards) > 0:
            available_strategies.add(PlayStrategy.PLAY_MINIMAL)

            if (
                len(CardPatternChecker.find_cards_with_count(
                    all_available_cards, 1))
                > 0
            ):
                available_strategies.add(PlayStrategy.SPLIT_SINGLE)

            if (
                len(CardPatternChecker.find_cards_with_count(
                    all_available_cards, 2))
                > 0
            ):
                available_strategies.add(PlayStrategy.SPLIT_PAIR)

            if (
                len(CardPatternChecker.find_cards_with_count(
                    all_available_cards, 3))
                > 0
            ):
                available_strategies.add(PlayStrategy.SPLIT_TRIPLE)

            if (
                len(CardPatternChecker.find_cards_with_count(
                    all_available_cards, 4))
                > 0
            ):
                available_strategies.add(PlayStrategy.SPLIT_QUAD)

            if (
                len(CardPatternChecker.find_cards_with_count(
                    all_available_cards, 5))
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
                    len(CardPatternChecker.find_cards_with_count(
                        all_no_split_cards, 1))
                    > 0
                ):
                    available_strategies.add(PlayStrategy.SINGLE)

                if (
                    len(CardPatternChecker.find_cards_with_count(
                        all_no_split_cards, 2))
                    > 0
                ):
                    available_strategies.add(PlayStrategy.PAIR)

                if (
                    len(CardPatternChecker.find_cards_with_count(
                        all_no_split_cards, 3))
                    > 0
                ):
                    available_strategies.add(PlayStrategy.TRIPLE)

                if (
                    len(CardPatternChecker.find_cards_with_count(
                        all_no_split_cards, 4))
                    > 0
                ):
                    available_strategies.add(PlayStrategy.QUAD)

                if (
                    len(CardPatternChecker.find_cards_with_count(
                        all_no_split_cards, 5))
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

    def select_strategy(self, player_id: int, strategy: PlayStrategy) -> List[Card]:
        """
        根据传入的策略，返回一组牌

        参数:
            player_id: 玩家ID
            strategy: 使用的策略

        返回:
            根据策略选择的一组牌
        """
        play_system = esper.get_processor(PlaySystem)

        if play_system is None:
            raise ValueError("PlaySystem not found")

        player_entity = play_system.get_player_entity_by_id(player_id)
        if player_entity is None:
            raise ValueError("Player not found")

        hand_cards = esper.component_for_entity(player_entity, Hand)
        last_played_cards = play_system.last_played_cards

        # 检查策略是否可用
        available_strategies = self.get_available_strategies(player_id)
        if strategy not in available_strategies:
            raise ValueError(f"Strategy {strategy} is not available")

        # 如果策略是PASS，则返回空列表
        if strategy == PlayStrategy.PASS:
            return []

        # 确定是否允许拆牌
        allow_split = strategy in {
            PlayStrategy.PLAY_MINIMAL,
            PlayStrategy.SPLIT_SINGLE,
            PlayStrategy.SPLIT_PAIR,
            PlayStrategy.SPLIT_TRIPLE,
            PlayStrategy.SPLIT_QUAD,
            PlayStrategy.SPLIT_PENTA,
            PlayStrategy.SPLIT_MULTI,
        }

        # 获取所有可能的牌组合
        if allow_split:
            all_combinations = CardPatternChecker.find_all_beating_combinations(
                hand_cards.cards, last_played_cards
            )
        else:
            all_combinations = (
                CardPatternChecker.find_all_beating_combinations_without_splitting(
                    hand_cards.cards, last_played_cards
                )
            )

        if not all_combinations:
            raise ValueError("No valid card combinations found")

        # 根据不同策略选择不同牌组
        if (
            strategy == PlayStrategy.PLAY_MINIMAL
            or strategy == PlayStrategy.PLAY_MINIMAL_INTACT
        ):
            # 选择最小的牌组合
            return min(
                all_combinations,
                key=lambda cards: sum(card.rank.get_value() for card in cards),
            )

        elif strategy in {PlayStrategy.SINGLE, PlayStrategy.SPLIT_SINGLE}:
            # 选择单张牌中最小的
            singles = CardPatternChecker.find_cards_with_count(
                all_combinations, 1)
            if not singles:
                raise ValueError("No single cards available")
            return min(singles, key=lambda cards: cards[0].rank.get_value())

        elif strategy in {PlayStrategy.PAIR, PlayStrategy.SPLIT_PAIR}:
            # 选择对子中最小的
            pairs = CardPatternChecker.find_cards_with_count(
                all_combinations, 2)
            if not pairs:
                raise ValueError("No pairs available")
            return min(pairs, key=lambda cards: cards[0].rank.get_value())

        elif strategy in {PlayStrategy.TRIPLE, PlayStrategy.SPLIT_TRIPLE}:
            # 选择三张牌中最小的
            triples = CardPatternChecker.find_cards_with_count(
                all_combinations, 3)
            if not triples:
                raise ValueError("No triples available")
            return min(triples, key=lambda cards: cards[0].rank.get_value())

        elif strategy in {PlayStrategy.QUAD, PlayStrategy.SPLIT_QUAD}:
            # 选择四张牌中最小的
            quads = CardPatternChecker.find_cards_with_count(
                all_combinations, 4)
            if not quads:
                raise ValueError("No quads available")
            return min(quads, key=lambda cards: cards[0].rank.get_value())

        elif strategy in {PlayStrategy.PENTA, PlayStrategy.SPLIT_PENTA}:
            # 选择五张牌中最小的
            pentas = CardPatternChecker.find_cards_with_count(
                all_combinations, 5)
            if not pentas:
                raise ValueError("No pentas available")
            return min(pentas, key=lambda cards: cards[0].rank.get_value())

        elif strategy in {PlayStrategy.MULTI, PlayStrategy.SPLIT_MULTI}:
            # 选择多张牌中最小的
            multis = CardPatternChecker.find_cards_with_count(
                all_combinations, 6, True)
            if not multis:
                raise ValueError("No multi-card combinations available")
            return min(
                multis, key=lambda cards: sum(
                    card.rank.get_value() for card in cards)
            )

        # 未知策略
        raise ValueError(f"Unknown strategy: {strategy}")
