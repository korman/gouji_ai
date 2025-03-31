import esper
import logging
import random
from ..interface import TurnHandlerInterface
from ..components import PlayerComponent, Hand, TeamComponent, Card
from ..utils import CardPatternChecker
from ..interface import PlayerAction
from typing import List, Tuple


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
            # 找出能压过上一手牌的组合
            beating_combinations = CardPatternChecker.find_all_beating_combinations(
                hand.cards, last_played_cards
            )

            if not beating_combinations:
                # 没有能压过的组合，选择 PASS
                # 循环输出last_played_cards

                if last_played_cards is not None:
                    logging.debug("上一手牌:")
                    for card in last_played_cards:
                        logging.debug(f"{card}")
                else:
                    logging.debug("上一手牌为空")

                return PlayerAction.PASS, []

            current_played_cards = random.choice(beating_combinations)

            # 打出选择的牌
            return PlayerAction.PLAY, current_played_cards
