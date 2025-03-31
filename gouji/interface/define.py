from enum import Enum  # 导入Enum类，用于创建枚举类型


class PlayerAction(Enum):
    """
    表示玩家可执行的动作类型的枚举。

    枚举值:
        PLAY: 玩家选择出牌
        PASS: 玩家选择跳过回合不出牌
    """

    PLAY = "出牌"  # 玩家选择出牌的动作
    PASS = "过牌"  # 玩家选择跳过回合不出牌的动作
