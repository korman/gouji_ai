from ..constants import Team


class PlayerComponent:
    """表示玩家的组件"""

    def __init__(self, name, player_id, is_ai=False):
        self.name = name
        self.player_id = player_id
        self.is_ai = is_ai


class TeamComponent:
    """表示玩家所属队伍的组件"""

    def __init__(self, team: Team):
        self.team = team
