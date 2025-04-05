import esper
import logging
import random
from ..interface import TurnHandlerInterface
from ..components import PlayerComponent, Hand, TeamComponent, Card
from ..utils import CardPatternChecker
from ..interface import PlayerAction
from typing import List, Tuple
from ..systems import StrategySystem
from ..constants import PlayStrategy


class DefaultAITurnHandler(TurnHandlerInterface):
    """
    默认AI回合处理器，实现基础的AI出牌逻辑
    """

    def handle_player_turn(
        self, game_state, player_id, play_system
    ) -> Tuple[PlayerAction, List[Card]]:
        """
        处理AI玩家的回合

        实现一个基础的AI出牌策略:
        1. 获取可出的牌
        2. 根据简单规则评估最佳出牌选择
        3. 使用出牌系统打出选中的牌

        参数:
            game_state: 游戏状态组件
            player_id: AI玩家ID
            play_system: 出牌系统的引用
        """
        # 获取当前玩家的手牌

        ai_entity = play_system.get_player_entity_by_id(player_id)

        if ai_entity is None:
            logging.debug(f"AI玩家 {player_id} 不存在")
            return

        player = esper.component_for_entity(ai_entity, PlayerComponent)
        hand = esper.component_for_entity(ai_entity, Hand)
        team = esper.component_for_entity(ai_entity, TeamComponent)
        last_played_cards = play_system.last_played_cards

        if hand:
            strategy_system: StrategySystem = esper.get_processor(
                StrategySystem)
            if strategy_system is None:
                raise ValueError("StrategySystem not found")

            available_strategies = strategy_system.get_available_strategies(
                player_id)

            # 随机选择一个策略
            selected_strategy = random.choice(list(available_strategies))
            select_strategy_cards: List[Card] = strategy_system.select_strategy(
                player_id, selected_strategy)

            if selected_strategy == PlayStrategy.PASS:
                return PlayerAction.PASS, []
            else:
                return PlayerAction.PLAY, select_strategy_cards
