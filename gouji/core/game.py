import esper
import logging
from ..components import PlayerComponent, Hand, TeamComponent, GameStateComponent
from ..systems import DeckSystem, DealSystem, PlaySystem, DatabaseSystem, StrategySystem
from ..constants import Team, ScoringRules
from ..interface import TurnHandlerInterface


class GoujiGame:
    """
    够级游戏主类，负责初始化游戏环境、创建游戏组件及运行游戏。

    该类是游戏的核心控制器，使用ECS(实体组件系统)架构管理游戏:
    1. 初始化游戏状态和玩家
    2. 创建并注册游戏系统处理器
    3. 提供游戏主循环逻辑
    4. 允许注册玩家回合处理器，决定玩家类型

    使用esper作为ECS框架来管理实体、组件和系统。
    """

    def __init__(self, world_name: str = "default"):
        """
        初始化游戏环境和组件。
        玩家类型(AI或人类)将根据注册的回合处理器类型决定。
        """

        # 保存世界名称
        self._world_name = world_name

        # 创建世界
        esper.switch_world(self._world_name)

        for world in esper.list_worlds():
            if world != self._world_name:
                esper.delete_world(world)

        # 创建游戏状态
        game_state_entity = esper.create_entity()
        esper.add_component(game_state_entity, GameStateComponent())

        # 初始化回合处理器字典
        self._turn_handlers = {}

        # 创建游戏玩家（初始默认全部为AI）
        self._create_players()

        # 初始化游戏系统
        self._deck_system = DeckSystem()
        self._deal_system = DealSystem(self._deck_system)
        self._play_system = PlaySystem()

        sqlite_db = DatabaseSystem()
        sqlite_db.record_training = False

        # 注册策略系统
        strategy_system = StrategySystem()

        # 添加处理器
        esper.add_processor(self._deck_system)
        esper.add_processor(self._deal_system)
        esper.add_processor(self._play_system)
        esper.add_processor(sqlite_db)
        esper.add_processor(strategy_system)

    def register_turn_handler(self, player_id, handler, is_human=None):
        """
        为指定玩家注册回合处理器并设置玩家类型

        Args:
            player_id (int): 玩家ID
            handler (TurnHandlerInterface): 回合处理器实例
            is_human (bool, optional): 是否为人类玩家。如果为None，则根据处理器类名自动判断

        Returns:
            bool: 注册是否成功
        """
        if not isinstance(handler, TurnHandlerInterface):
            logging.error(f"错误: 处理器必须实现TurnHandlerInterface接口")
            return False

        # 检查玩家ID是否有效，同时查找PlayerComponent
        player_found = False
        player_component = None

        for entity, component in esper.get_component(PlayerComponent):
            if component.player_id == player_id:
                player_found = True
                player_component = component
                break

        if not player_found or not player_component:
            logging.error(f"错误: 玩家ID {player_id} 不存在")
            return False

        # 判断玩家类型（如果未显式指定，则根据处理器类名判断）
        if is_human is None:
            handler_class_name = handler.__class__.__name__.lower()
            is_human = "human" in handler_class_name or "player" in handler_class_name

        # 更新玩家类型
        player_component.is_ai = not is_human

        # 注册处理器
        self._turn_handlers[player_id] = handler
        # print(f"成功为玩家 {player_id} 注册了回合处理器: {handler.__class__.__name__}")
        # print(
        #     f"玩家 {player_id} 现在是{'人类' if not player_component.is_ai else 'AI'}玩家"
        # )

        if self._play_system is not None:
            self._play_system.register_turn_handler(player_id, handler)

        return True

    def register_handler_for_player(self, player_id, handler):
        """
        为单个玩家注册处理器实例

        Args:
            player_id (int): 玩家ID
            handler: 处理器实例
        """
        self.register_turn_handler(player_id, handler)

    #    print(f"已为玩家 {player_id} 注册处理器: {handler.__class__.__name__}")

    def register_handlers_for_players(
        self, player_ids, handler_class, **handler_kwargs
    ):
        """
        为多个玩家注册同一类型的处理器

        Args:
            player_ids (list): 玩家ID列表
            handler_class: 处理器类
            **handler_kwargs: 传递给处理器构造函数的关键字参数
        """
        for player_id in player_ids:
            # 创建处理器实例
            handler = handler_class(**handler_kwargs)
            self.register_turn_handler(player_id, handler)

    #  print(f"已为 {len(player_ids)} 名玩家注册处理器: {handler_class.__name__}")

    def _create_players(self):
        """
        创建游戏中的玩家实体。
        所有玩家初始设置为AI玩家，具体类型将根据注册的处理器决定
        """
        # 创建6个玩家，交替分配队伍
        for i in range(6):
            player_entity = esper.create_entity()

            # 初始默认为AI玩家
            is_ai = True

            name = f"Player{i+1}"

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
        # 检查每个玩家是否都有回合处理器
        missing_handlers = []
        for _, component in esper.get_component(PlayerComponent):
            if component.player_id not in self._turn_handlers:
                missing_handlers.append(component.player_id)

        if missing_handlers:
            logging.error(f"警告: 以下玩家没有注册回合处理器: {missing_handlers}")
            response = input("是否继续游戏? (y/n): ")
            if response.lower() != "y":
                logging.warning("游戏已取消")
                return

        # 输出玩家信息
        # print("\n玩家信息:")
        # for _, component in esper.get_component(PlayerComponent):
        #     print(
        #         f"玩家{component.player_id+1} ({component.name}): {'AI' if component.is_ai else '人类'}"
        #     )
        # print()

        # print("够级游戏开始！")

        # 处理发牌
        esper.process()

        # 获取游戏状态组件
        game_state = None
        for _, state in esper.get_component(GameStateComponent):
            game_state = state
            break

        if not game_state:
            logging.error("错误：找不到游戏状态组件")
            return

        while True:
            try:
                # 处理出牌
                esper.process()

                # 检查游戏是否结束
                if game_state.phase == "game_over":
                    teamA_score = 0
                    teamB_score = 0

                    logging.debug("游戏结束！排名情况:")
                    for rank, player_id in enumerate(game_state.rankings):
                        player_name = self._play_system.get_player_name_by_id(player_id)

                        # 获取该玩家的PlayerComponent 和 TeamComponent
                        player_component = None

                        # 根据排名计算分数
                        score_change = ScoringRules.get_score_by_rank(rank)

                        for _, (component, team_component) in esper.get_components(
                            PlayerComponent, TeamComponent
                        ):
                            if component.player_id == player_id:
                                player_component = component
                                if team_component.team == Team.A:
                                    teamA_score += score_change
                                # print(f"teamA_score: {teamA_score}")
                                else:
                                    teamB_score += score_change
                                # print(f"teamB_score: {teamB_score}")
                                break

                        # 更新玩家分数
                        if player_component:
                            player_component.score += score_change
                            # print(
                            #     f"第{rank+1}名: {player_name} (分数变化: {'+' if score_change >= 0 else ''}{score_change})"
                            # )

                    # 找出最后一名
                    if len(game_state.rankings) == 5:
                        last_player_id = next(
                            id for id in range(6) if id not in game_state.rankings
                        )

                        # 获得最后一名玩家的PlayerComponent与TeamComponent
                        for _, (component, team_component) in esper.get_components(
                            PlayerComponent, TeamComponent
                        ):
                            if component.player_id == last_player_id:
                                if team_component.team == Team.A:
                                    teamA_score -= 2
                                else:
                                    teamB_score -= 2
                                break

                        last_player_name = self._play_system.get_player_name_by_id(
                            last_player_id
                        )
                        # print(f"最后一名: {last_player_name}")

                    # 根据teamA_score和teamB_score判断胜负
                    # if teamA_score > teamB_score:
                    #     print(
                    #         f"队伍A获胜！ A队得分: {teamA_score}, B队得分: {teamB_score}"
                    #     )
                    # elif teamA_score < teamB_score:
                    #     print(
                    #         f"队伍B获胜！ A队得分: {teamA_score}, B队得分: {teamB_score}"
                    #     )
                    # else:
                    #     print(f"平局！ A队得分: {teamA_score}, B队得分: {teamB_score}")

                    break

            except KeyboardInterrupt:
                logging.warning("\n游戏被用户中断")
                break

        logging.debug("感谢您游玩够级游戏！")
