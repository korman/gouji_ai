from ..constants import Team


class PlayerComponent:
    """表示玩家的组件"""

    def __init__(self, name, player_id, is_ai=False):
        self._name = name
        self._player_id = player_id
        self._is_ai = is_ai
        self._score = 0

    @property
    def name(self):
        return self._name

    @property
    def player_id(self):
        return self._player_id

    @property
    def is_ai(self):
        return self._is_ai

    @is_ai.setter
    def is_ai(self, value):
        self._is_ai = value

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value


class TeamComponent:
    """表示玩家所属队伍的组件"""

    def __init__(self, team: Team):
        self._team = team

    @property
    def team(self):
        return self._team
