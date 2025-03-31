class GameStateComponent:
    """表示游戏状态的组件，管理游戏进行的各个阶段和玩家状态"""

    def __init__(self):
        self._phase = (
            "dealing"  # 游戏阶段：dealing(发牌), playing(出牌), game_over(结束)
        )
        self._current_player_id = 0  # 当前玩家ID，表示轮到哪位玩家操作
        self._human_player_id = -1  # 人类玩家ID (默认为-1，表示未设置)
        self._players_without_cards = set()  # 记录已经出完牌的玩家ID集合
        self._rankings = []  # 记录玩家完成顺序的列表，按出完牌的先后排序

    @property
    def rankings(self):
        """获取玩家完成游戏的排名列表"""
        return self._rankings

    @property
    def players_without_cards(self):
        """获取已经出完牌的玩家ID集合"""
        return self._players_without_cards

    @property
    def current_player_id(self):
        """获取当前轮到的玩家ID"""
        return self._current_player_id

    @current_player_id.setter
    def current_player_id(self, player_id):
        """设置当前轮到的玩家ID

        Args:
            player_id: 玩家的唯一标识符
        """
        self._current_player_id = player_id

    @property
    def human_player_id(self):
        """获取人类玩家的ID"""
        return self._human_player_id

    @property
    def phase(self):
        """获取当前游戏阶段"""
        return self._phase

    @phase.setter
    def phase(self, phase):
        """设置当前游戏阶段

        Args:
            phase: 游戏阶段，可能的值包括dealing(发牌)、playing(出牌)、game_over(结束)
        """
        self._phase = phase
