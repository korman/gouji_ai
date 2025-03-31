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

        # # 首出牌（上家无牌）
        # if previous_cards is None or len(previous_cards) == 0:
        #     # 检查各种出牌可能性
        #     if PlayStrategyGenerator.has_singles(hand_cards):
        #         available_strategies.add(PlayStrategy.SINGLE_PLAY)
        #         available_strategies.add(PlayStrategy.PLAY_MINIMAL)

        #     if PlayStrategyGenerator.has_multiples(hand_cards):
        #         available_strategies.add(PlayStrategy.PLAY_MINIMAL)

        #     if PlayStrategyGenerator.has_bomb(hand_cards):
        #         available_strategies.add(PlayStrategy.BOMB_PLAY)

        #     if PlayStrategyGenerator.has_long_group(hand_cards):
        #         available_strategies.add(PlayStrategy.LONG_CHAIN_PLAY)

        #     if PlayStrategyGenerator.has_big_joker(hand_cards):
        #         available_strategies.add(PlayStrategy.BIG_JOKER_PLAY)

        #     if PlayStrategyGenerator.has_small_joker(hand_cards):
        #         available_strategies.add(PlayStrategy.SMALL_JOKER_PLAY)

        # # 跟牌（需要压制上家牌）
        # else:
        #     # 过牌始终是一个选项
        #     available_strategies.add(PlayStrategy.PASS)

        #     # 处理单张牌的情况
        #     if len(previous_cards) == 1:
        #         prev_value = previous_cards[0]._rank.get_value()

        #         # 检查是否有更大的单牌
        #         if PlayStrategyGenerator.can_beat_with_single(hand_cards, prev_value):
        #             available_strategies.add(PlayStrategy.SINGLE_PLAY)

        #         # 检查是否有大王
        #         if PlayStrategyGenerator.has_big_joker(hand_cards):
        #             available_strategies.add(PlayStrategy.BIG_JOKER_PLAY)

        #         # 检查是否有小王，且上家不是大王
        #         # 假设大王值为17
        #         if PlayStrategyGenerator.has_small_joker(hand_cards) and prev_value < 17:
        #             available_strategies.add(PlayStrategy.SMALL_JOKER_PLAY)

        #     # 处理多张牌的情况
        #     elif len(previous_cards) > 0:
        #         prev_pattern_value = previous_cards[0]._rank.get_value()
        #         prev_pattern_count = len(previous_cards)

        #         # 检查是否可以使用同数量但更大点数的牌压制
        #         if PlayStrategyGenerator.can_beat_with_same_count(hand_cards, prev_pattern_count, prev_pattern_value):
        #             available_strategies.add(PlayStrategy.PLAY_MINIMAL)

        #         # 检查是否需要拆牌来压制
        #         if PlayStrategyGenerator.need_split_to_beat(hand_cards, prev_pattern_count, prev_pattern_value):
        #             available_strategies.add(PlayStrategy.SPLIT_PLAY)

        #         # 特殊规则: 小王可以压制炸弹(牌值为2)
        #         if PlayStrategyGenerator.has_small_joker(hand_cards) and prev_pattern_count == 4 and prev_pattern_value == 2:
        #             available_strategies.add(PlayStrategy.SMALL_JOKER_PLAY)

        #         # 特殊规则: 大王可以压制小王
        #         # 假设小王值为16
        #         if PlayStrategyGenerator.has_big_joker(hand_cards) and prev_pattern_count == 1 and prev_pattern_value == 16:
        #             available_strategies.add(PlayStrategy.BIG_JOKER_PLAY)

        #         # 如果上一手牌是5张以上，检查是否有更大的同等数量牌组
        #         if prev_pattern_count >= 5 and PlayStrategyGenerator.can_beat_with_same_count(hand_cards, prev_pattern_count, prev_pattern_value):
        #             available_strategies.add(PlayStrategy.LONG_CHAIN_PLAY)

        return available_strategies
