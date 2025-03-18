from ..interface import TurnHandlerInterface


class HumanPlayerTurnHandler(TurnHandlerInterface):
    """
    人类玩家回合处理器，允许用户通过命令行交互方式出牌
    """

    def handle_player_turn(self, game_state, player_id, play_system):
        """
        处理人类玩家的回合，提供交互式界面

        参数:
            game_state: 游戏状态组件
            player_id: 当前玩家ID
            play_system: 出牌系统的引用
        """
        # 显示游戏状态信息
        self._display_game_status(game_state, player_id)

        # 获取玩家手牌
        player_hand = game_state.get_player_hand(player_id)

        if not player_hand:
            print(f"您没有手牌可出。")
            time.sleep(1.5)  # 暂停一小段时间让玩家看到信息
            return

        # 显示玩家手牌
        self._display_player_hand(player_hand)

        # 获取可打出的牌
        playable_cards = self._get_playable_cards(
            game_state, player_id, player_hand, play_system
        )

        if not playable_cards:
            print("您没有可出的牌，自动跳过回合。")
            time.sleep(1.5)

            if hasattr(play_system, "pass_turn"):
                play_system.pass_turn(player_id)
            return

        # 让玩家选择操作
        selected_action = self._get_player_action(player_hand, playable_cards)

        # 执行选择的操作
        if selected_action.lower() == "p" or selected_action.lower() == "pass":
            print("您选择了跳过回合。")
            if hasattr(play_system, "pass_turn"):
                play_system.pass_turn(player_id)
        else:
            try:
                card_index = int(selected_action) - 1  # 由于显示从1开始，索引需要减1
                if 0 <= card_index < len(player_hand):
                    selected_card = player_hand[card_index]
                    if selected_card in playable_cards:
                        print(f"您打出了: {selected_card}")
                        play_system.play_card(player_id, selected_card)
                    else:
                        print("该牌不能打出！请重新选择。")
                        time.sleep(1)
                        self.handle_player_turn(
                            game_state, player_id, play_system
                        )  # 重新开始回合
                else:
                    print("无效的选择！请重新选择。")
                    time.sleep(1)
                    self.handle_player_turn(
                        game_state, player_id, play_system
                    )  # 重新开始回合
            except ValueError:
                print("无效的输入！请重新选择。")
                time.sleep(1)
                self.handle_player_turn(
                    game_state, player_id, play_system
                )  # 重新开始回合

    def _display_game_status(self, game_state, player_id):
        """
        显示当前游戏状态

        参数:
            game_state: 游戏状态组件
            player_id: 当前玩家ID
        """
        print("\n" + "=" * 50)
        print(f"玩家 {player_id} 的回合")
        print("=" * 50)

        # 显示其他游戏信息（如果有）
        if hasattr(game_state, "get_game_info"):
            game_info = game_state.get_game_info()
            print("游戏信息:")
            print(game_info)

        # 显示当前桌面牌（如果有）
        if hasattr(game_state, "get_current_card") and callable(
            game_state.get_current_card
        ):
            current_card = game_state.get_current_card()
            if current_card:
                print(f"当前桌面牌: {current_card}")

        # 显示其他玩家信息
        if hasattr(game_state, "get_players_info") and callable(
            game_state.get_players_info
        ):
            players_info = game_state.get_players_info()
            print("\n其他玩家信息:")
            for p_id, info in players_info.items():
                if p_id != player_id:  # 不显示当前玩家信息
                    cards_count = (
                        len(info.get("hand", [])) if isinstance(info, dict) else "未知"
                    )
                    print(f"玩家 {p_id}: {cards_count} 张牌")

        print("-" * 50)

    def _display_player_hand(self, player_hand):
        """
        显示玩家手牌

        参数:
            player_hand: 玩家手牌列表
        """
        print("\n您的手牌:")
        for i, card in enumerate(player_hand, 1):
            print(f"{i}. {card}")
        print("-" * 50)

    def _get_playable_cards(self, game_state, player_id, player_hand, play_system):
        """
        获取玩家当前可以打出的牌

        参数:
            game_state: 游戏状态
            player_id: 玩家ID
            player_hand: 玩家手牌
            play_system: 出牌系统

        返回:
            列表: 可打出的牌列表
        """
        playable_cards = []

        # 如果系统提供了检查牌是否可出的方法，使用它
        if hasattr(play_system, "is_card_playable") and callable(
            play_system.is_card_playable
        ):
            for card in player_hand:
                if play_system.is_card_playable(player_id, card, game_state):
                    playable_cards.append(card)
        else:
            # 默认情况下假设所有牌都可以打出
            playable_cards = player_hand.copy()

        return playable_cards

    def _get_player_action(self, player_hand, playable_cards):
        """
        获取玩家选择的操作

        参数:
            player_hand: 玩家手牌
            playable_cards: 可打出的牌列表

        返回:
            字符串: 玩家选择的操作
        """
        # 标记哪些牌可以打出
        print("\n可打出的牌:")
        for i, card in enumerate(player_hand, 1):
            if card in playable_cards:
                print(f"{i}. {card} [可出]")
            else:
                print(f"{i}. {card} [不可出]")

        # 显示可选操作
        print("\n请选择操作:")
        print("输入卡牌编号(1-{})出牌，或输入 'P' 跳过回合:".format(len(player_hand)))

        return input("请输入您的选择: ").strip()
