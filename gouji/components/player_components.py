from ..constants import Team  # 从constants模块导入Team枚举，用于表示玩家队伍


class PlayerComponent:
    """表示玩家的组件"""

    def __init__(self, name, player_id, is_ai=False):
        """
        初始化一个玩家组件。

        参数:
            name: 玩家的名称
            player_id: 玩家的唯一标识符
            is_ai: 是否为AI玩家，默认为False
        """
        self._name = name  # 玩家名称
        self._player_id = player_id  # 玩家唯一ID
        self._is_ai = is_ai  # 是否为AI玩家
        self._score = 0  # 玩家当前得分，初始为0

    @property
    def name(self):
        """
        获取玩家名称。

        返回:
            str: 玩家的名称
        """
        return self._name

    @property
    def player_id(self):
        """
        获取玩家ID。

        返回:
            int: 玩家的唯一标识符
        """
        return self._player_id

    @property
    def is_ai(self):
        """
        检查玩家是否为AI。

        返回:
            bool: 如果是AI玩家则为True，否则为False
        """
        return self._is_ai

    @is_ai.setter
    def is_ai(self, value):
        """
        设置玩家的AI状态。

        参数:
            value (bool): 玩家的AI状态，True表示是AI，False表示不是
        """
        self._is_ai = value

    @property
    def score(self):
        """
        获取玩家当前得分。

        返回:
            int: 玩家的当前得分
        """
        return self._score

    @score.setter
    def score(self, value):
        """
        设置玩家得分。

        参数:
            value (int): 要设置的新得分值
        """
        self._score = value


class TeamComponent:
    """表示玩家所属队伍的组件"""

    def __init__(self, team: Team):
        """
        初始化一个队伍组件。

        参数:
            team (Team): 队伍枚举值，表示玩家所属的队伍
        """
        self._team = team  # 玩家所属的队伍

    @property
    def team(self):
        """
        获取玩家所属的队伍。

        返回:
            Team: 表示队伍的枚举值
        """
        return self._team
