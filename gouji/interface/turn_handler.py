from abc import ABC, abstractmethod


class TurnHandlerInterface(ABC):
    """
    回合处理器接口，用于处理玩家回合的外部回调
    """

    @abstractmethod
    def handle_player_turn(self, game_state, player_id, play_system):
        """
        处理玩家回合

        参数:
            game_state: 游戏状态组件
            player_id: 当前玩家ID
            play_system: 出牌系统的引用，用于访问其方法和属性
        """
        pass
