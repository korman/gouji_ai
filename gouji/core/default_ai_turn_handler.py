from ..interface import TurnHandlerInterface


class DefaultAITurnHandler(TurnHandlerInterface):
    """
    默认AI回合处理器，实现基础的AI出牌逻辑
    """

    def handle_player_turn(self, game_state, player_id, play_system):
        """
        处理AI玩家的回合

        实现一个基础的AI出牌策略:
        1. 获取可出的牌
        2. 根据简单规则评估最佳出牌选择
        3. 使用出牌系统打出选中的牌

        参数:
            game_state: 游戏状态组件
            player_id: AI玩家ID
            play_system: 出牌系统的引用
        """
        # 获取当前玩家的手牌
        player_hand = game_state.get_player_hand(player_id)

        if not player_hand:
            # 手牌为空，无法出牌
            print(f"AI玩家 {player_id} 没有手牌可出")
            return

        # 获取当前可打出的合法牌
        playable_cards = self._get_playable_cards(
            game_state, player_id, player_hand, play_system)

        if not playable_cards:
            # 没有可出的牌，可能需要跳过回合
            print(f"AI玩家 {player_id} 没有可出的牌，跳过回合")
            play_system.pass_turn(player_id)
            return

        # 选择最佳出牌
        best_card = self._select_best_card(
            game_state, player_id, playable_cards, play_system)

        # 打出选择的牌
        print(f"AI玩家 {player_id} 打出: {best_card}")
        play_system.play_card(player_id, best_card)

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
        # 假设play_system有一个方法可以检查牌是否可以打出
        playable_cards = []
        for card in player_hand:
            if play_system.is_card_playable(player_id, card, game_state):
                playable_cards.append(card)

        return playable_cards

    def _select_best_card(self, game_state, player_id, playable_cards, play_system):
        """
        从可出的牌中选择最佳的一张

        参数:
            game_state: 游戏状态
            player_id: 玩家ID
            playable_cards: 可打出的牌列表
            play_system: 出牌系统

        返回:
            最佳的牌
        """
        # 如果只有一张牌可出，直接返回
        if len(playable_cards) == 1:
            return playable_cards[0]

        # 基础AI策略：尝试评估每张牌的价值并选择最高的
        card_values = {}
        for card in playable_cards:
            # 计算卡牌价值（这里需要根据具体游戏规则定制）
            value = self._evaluate_card_value(
                card, game_state, player_id, play_system)
            card_values[card] = value

        # 返回价值最高的牌
        return max(card_values, key=card_values.get)

    def _evaluate_card_value(self, card, game_state, player_id, play_system):
        """
        评估卡牌的价值

        参数:
            card: 要评估的卡牌
            game_state: 游戏状态
            player_id: 玩家ID
            play_system: 出牌系统

        返回:
            卡牌的数值评估（越高越好）
        """
        # 默认实现：简单模拟出牌后的效果
        # 注：这是一个示例实现，需要根据实际游戏规则定制

        # 假设卡牌有一个"power"或"value"属性表示强度
        # 如果没有，可以基于卡牌的其他属性计算价值
        try:
            # 尝试获取卡牌的基础价值
            base_value = getattr(card, "value", 0)

            # 可以添加额外评估规则，比如：
            # - 是否能消除对手的优势
            # - 是否会给我方带来特殊效果
            # - 是否能减少对手的选择

            # 这里只是一个简单实现，实际应用中应该基于游戏规则扩展
            return base_value

        except Exception as e:
            # 出错时给一个默认值
            print(f"评估卡牌价值时出错: {e}")
            return 1  # 默认价值
