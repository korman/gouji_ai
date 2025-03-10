import esper
from ..components import PlayerComponent, Hand, TeamComponent, GameStateComponent
from ..systems import DeckSystem, DealSystem, PlaySystem
from ..constants import Team, ScoringRules


class GoujiGame:
    """
    够级游戏主类，负责初始化游戏环境、创建游戏组件及运行游戏。

    该类是游戏的核心控制器，使用ECS(实体组件系统)架构管理游戏:
    1. 初始化游戏状态和玩家
    2. 创建并注册游戏系统处理器
    3. 提供游戏主循环逻辑

    使用esper作为ECS框架来管理实体、组件和系统。
    """

    def __init__(self, human_players=0):
        """
        初始化游戏环境和组件。

        Args:
            human_players (int, optional): 人类玩家数量. 默认为0 (全AI).
                                           最大值为6，超出范围会被调整.
        """
        # 重置esper世界状态（防止重复运行时的问题）
        esper.clear_database()

        # 创建游戏状态
        game_state_entity = esper.create_entity()
        esper.add_component(game_state_entity, GameStateComponent())

        # 根据传入的人类玩家数量创建玩家
        self.create_players(human_players)

        # 初始化游戏系统
        self.deck_system = DeckSystem()
        self.deal_system = DealSystem(self.deck_system)
        self.play_system = PlaySystem()

        # 添加处理器
        esper.add_processor(self.deck_system)
        esper.add_processor(self.deal_system)
        esper.add_processor(self.play_system)

    def create_players(self, human_players=0):
        """
        创建游戏中的玩家实体。

        Args:
            human_players (int, optional): 人类玩家数量. 默认为0.
                                           如果超过6，则调整为6.
        """
        # 限制人类玩家数量在0-6之间
        human_players = max(0, min(human_players, 6))

        # 创建6个玩家，交替分配队伍和玩家类型
        for i in range(6):
            player_entity = esper.create_entity()

            # 配置是否为AI
            is_ai = (i >= human_players)

            # 输出是否为AI
            print(f"玩家{i+1} 是{'AI' if is_ai else '人类'}")

            name = f"玩家{i+1}" if i < human_players else f"Player{i+1}"

            esper.add_component(player_entity, PlayerComponent(name, i, is_ai))
            esper.add_component(player_entity, Hand())

            # 交替分配队伍 (0,2,4为A队；1,3,5为B队)
            team = Team.A if i % 2 == 0 else Team.B
            esper.add_component(player_entity, TeamComponent(team))

    def run(self):
        """
        运行游戏的主循环。

        游戏流程:
        1. 首先进行一次处理器轮转，处理发牌阶段
        2. 然后进入主循环，反复处理玩家出牌
        3. 仅在轮到人类玩家时展示交互提示
        4. 捕获KeyboardInterrupt以便用户可以使用Ctrl+C退出游戏
        """
        print("够级游戏开始！")

        # 处理发牌
        esper.process()

        # 获取游戏状态组件
        game_state = None
        for _, state in esper.get_component(GameStateComponent):
            game_state = state
            break

        if not game_state:
            print("错误：找不到游戏状态组件")
            return

        while True:
            try:
                # 处理出牌
                esper.process()

                # 检查游戏是否结束
                if game_state.phase == "game_over":
                    teamA_score = 0
                    teamB_score = 0

                    print("游戏结束！排名情况:")
                    for rank, player_id in enumerate(game_state.rankings):
                        player_name = self.play_system.get_player_name_by_id(
                            player_id)

                        # 获取该玩家的PlayerComponent 和 TeamComponent
                        player_component = None

                        # 根据排名计算分数
                        score_change = ScoringRules.get_score_by_rank(rank)

                        for _, (component, team_component) in esper.get_components(PlayerComponent, TeamComponent):
                            if component.player_id == player_id:
                                player_component = component
                                if team_component.team == Team.A:
                                    teamA_score += score_change
                                    print(f"teamA_score: {teamA_score}")
                                else:
                                    teamB_score += score_change
                                    print(f"teamB_score: {teamB_score}")
                                break

                        # 更新玩家分数
                        if player_component:
                            player_component.score += score_change
                            print(
                                f"第{rank+1}名: {player_name} (分数变化: {'+' if score_change >= 0 else ''}{score_change})")

                    # 找出最后一名
                    if len(game_state.rankings) == 5:
                        last_player_id = next(id for id in range(
                            6) if id not in game_state.rankings)

                        # 获得最后一名玩家的PlayerComponent与TeamComponent
                        for _, (component, team_component) in esper.get_components(PlayerComponent, TeamComponent):
                            if component.player_id == last_player_id:
                                if team_component.team == Team.A:
                                    teamA_score -= 2
                                else:
                                    teamB_score -= 2
                                break

                        last_player_name = self.play_system.get_player_name_by_id(
                            last_player_id)
                        print(f"最后一名: {last_player_name}")

                    # 根据teamA_score和teamB_score判断胜负
                    if teamA_score > teamB_score:
                        print(
                            f"队伍A获胜！ A队得分: {teamA_score}, B队得分: {teamB_score}")
                    elif teamA_score < teamB_score:
                        print(
                            f"队伍B获胜！ A队得分: {teamA_score}, B队得分: {teamB_score}")
                    else:
                        print(f"平局！ A队得分: {teamA_score}, B队得分: {teamB_score}")

                    break

            except KeyboardInterrupt:
                print("\n游戏被用户中断")
                break

        print("感谢您游玩够级游戏！")
