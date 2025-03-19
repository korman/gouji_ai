import time
from ..components import Card
from ..interface import TurnHandlerInterface
from ..interface import PlayerAction
from typing import List, Tuple


class HumanPlayerTurnHandler(TurnHandlerInterface):
    """
    人类玩家回合处理器，允许用户通过命令行交互方式出牌
    """

    def handle_player_turn(
        self, game_state, player_id, play_system
    ) -> Tuple[PlayerAction, List[Card]]:
        """
        处理人类玩家的回合，提供交互式界面

        参数:
            game_state: 游戏状态组件
            player_id: 当前玩家ID
            play_system: 出牌系统的引用
        """
        pass
