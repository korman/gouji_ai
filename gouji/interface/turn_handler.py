from abc import ABC, abstractmethod
from ..components import Card
from typing import Tuple, List
from .define import PlayerAction


class TurnHandlerInterface(ABC):
    """
    回合处理器接口，用于处理玩家回合的外部回调
    """

    @abstractmethod
    def handle_player_turn(
        self, game_state, player_id, play_system
    ) -> Tuple[PlayerAction, List[Card]]:
        """
        处理玩家回合

        参数:
            game_state: 游戏状态组件
            player_id: 当前玩家ID
            play_system: 出牌系统的引用，用于访问其方法和属性

        返回:
            Tuple[PlayerAction, List[Card]]: 玩家选择的动作和出的牌列表
                - PlayerAction: 玩家的动作（PLAY 或 PASS）
                - List[Card]: 玩家出的牌列表（如果选择 PASS，则可以为空）
        """
        pass

    def on_game_end(self, game_state=None, rankings=None):
        """
        游戏结束时的回调方法，用于清理状态或进行学习

        参数:
            game_state: 可选，游戏结束时的状态组件
            rankings: 可选，游戏结束时的玩家排名列表

        这是一个可选实现的方法，有学习需求的AI处理器应覆盖此方法。
        """
        pass
