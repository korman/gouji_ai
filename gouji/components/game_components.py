class GameStateComponent:
    """表示游戏状态的组件"""

    def __init__(self):
        self.phase = "dealing"  # 游戏阶段：dealing(发牌), playing(出牌), game_over(结束)
        self.current_player_id = 0  # 当前玩家ID
        self.human_player_id = -1  # 人类玩家ID (默认为0)
        self.players_without_cards = set()  # 记录已经出完牌的玩家ID
        self.rankings = []  # 记录玩家完成顺序
