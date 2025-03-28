class GameStateComponent:
    """表示游戏状态的组件"""

    def __init__(self):
        self._phase = (
            "dealing"  # 游戏阶段：dealing(发牌), playing(出牌), game_over(结束)
        )
        self._current_player_id = 0  # 当前玩家ID
        self._human_player_id = -1  # 人类玩家ID (默认为0)
        self._players_without_cards = set()  # 记录已经出完牌的玩家ID
        self._rankings = []  # 记录玩家完成顺序

    @property
    def rankings(self):
        return self._rankings

    @property
    def players_without_cards(self):
        return self._players_without_cards

    @property
    def current_player_id(self):
        return self._current_player_id

    @current_player_id.setter
    def current_player_id(self, player_id):
        self._current_player_id = player_id

    @property
    def human_player_id(self):
        return self._human_player_id

    @property
    def phase(self):
        return self._phase

    @phase.setter
    def phase(self, phase):
        self._phase = phase
