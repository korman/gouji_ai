import esper
import random
from typing import List, Dict
from collections import defaultdict
from ..components.card_components import Card, Hand
from ..components.player_components import PlayerComponent, TeamComponent
from ..components.game_components import GameStateComponent
from ..constants import Rank


class PlaySystem(esper.Processor):
    """
    出牌系统处理器，负责管理游戏中的出牌流程和玩家回合。

    继承自esper.Processor，作为ECS架构中的处理器组件。
    该系统处理游戏的核心玩法，包括人类玩家和AI玩家的出牌逻辑、
    手牌管理和回合转换。根据当前游戏状态确定是谁的回合，
    并相应地执行人类交互或AI决策。
    """

    def process(self):
        """
        处理器的主要执行方法，由ECS系统自动调用。

        检查游戏是否处于出牌阶段("playing")，然后根据当前玩家是
        人类还是AI，调用相应的处理方法。
        """
        # 只有在出牌阶段才处理
        for _, game_state in esper.get_component(GameStateComponent):
            if game_state.phase == "playing":
                # 检查是否只剩最后一名玩家（额外检查，以防其他地方遗漏）
                if len(game_state.players_without_cards) == 5:
                    last_player_id = next(id for id in range(
                        6) if id not in game_state.players_without_cards)
                    last_player_name = self.get_player_name_by_id(
                        last_player_id)
                    print(f"\n🎮 游戏结束! {last_player_name} 成为最后一名!")
                    game_state.phase = "game_over"
                    return

                # 轮到人类玩家，显示手牌
                if game_state.current_player_id == game_state.human_player_id:
                    self.handle_human_turn(game_state)
                else:
                    # AI玩家出牌
                    self.handle_ai_turn(game_state)

    def handle_human_turn(self, game_state):
        """
        处理人类玩家回合。

        显示玩家的手牌，允许玩家选择要出的牌，
        然后更新游戏状态到下一个玩家的回合。

        参数:
            game_state (GameStateComponent): 当前游戏状态组件
        """
        human_entity = self.get_player_entity_by_id(game_state.human_player_id)

        if human_entity is not None:
            # 正确地获取各个组件
            player = esper.component_for_entity(human_entity, PlayerComponent)
            hand = esper.component_for_entity(human_entity, Hand)
            team = esper.component_for_entity(human_entity, TeamComponent)

            # 显示玩家手牌
            self.display_hand(player, hand)

            # 让玩家出牌
            if hand.cards:
                self.player_play_card(player, hand, team)
                # 检查是否出完所有牌
                if not hand.cards:
                    print(
                        f"\n🎉 {player.name} ({team.team.name}队) 出完了所有牌，排名第{len(game_state.rankings) + 1}!")
                    game_state.players_without_cards.add(
                        game_state.human_player_id)
                    game_state.rankings.append(game_state.human_player_id)

                    # 检查是否只剩最后一名玩家
                    if len(game_state.players_without_cards) == 5:
                        # 找出最后一名
                        last_player_id = next(id for id in range(
                            6) if id not in game_state.players_without_cards)
                        last_player_name = self.get_player_name_by_id(
                            last_player_id)
                        print(f"\n🎮 游戏结束! {last_player_name} 成为最后一名!")
                        game_state.phase = "game_over"
                        return
            else:
                print(f"\n{player.name} 没有牌了!")

            # 更新下一个玩家
            game_state.current_player_id = self.find_next_player_with_cards(
                game_state)

            # 提示等待下一个AI玩家
            next_player_name = self.get_player_name_by_id(
                game_state.current_player_id)
            print(f"\n等待 {next_player_name} 出牌...")

    def handle_ai_turn(self, game_state):
        """
        处理AI玩家回合。

        获取AI玩家的手牌，随机选择一张牌打出，
        然后更新游戏状态到下一个玩家的回合。

        参数:
            game_state (GameStateComponent): 当前游戏状态组件
        """
        ai_entity = self.get_player_entity_by_id(game_state.current_player_id)

        if ai_entity is not None:
            # 正确地获取各个组件
            player = esper.component_for_entity(ai_entity, PlayerComponent)
            hand = esper.component_for_entity(ai_entity, Hand)
            team = esper.component_for_entity(ai_entity, TeamComponent)

            # AI随机出牌
            if hand.cards:
                card_index = random.randint(0, len(hand.cards) - 1)
                played_card = hand.cards.pop(card_index)
                print(f"\n{player.name} ({team.team.name}队) 打出了: {played_card}")

                # 检查是否出完所有牌
                if not hand.cards:
                    print(
                        f"\n🏆 {player.name} ({team.team.name}队) 出完了所有牌，排名第{len(game_state.rankings) + 1}!")
                    game_state.players_without_cards.add(
                        game_state.current_player_id)
                    game_state.rankings.append(game_state.current_player_id)

                    # 检查是否只剩最后一名玩家
                    if len(game_state.players_without_cards) == 5:
                        # 找出最后一名
                        last_player_id = next(id for id in range(
                            6) if id not in game_state.players_without_cards)
                        last_player_name = self.get_player_name_by_id(
                            last_player_id)
                        print(f"\n🎮 游戏结束! {last_player_name} 成为最后一名!")
                        game_state.phase = "game_over"
                        return
            else:
                print(f"\n{player.name} 没有牌了!")

            # 更新下一个玩家 - 使用新的查找函数
            game_state.current_player_id = self.find_next_player_with_cards(
                game_state)

            # 如果下一个玩家是人类，提示并显示手牌
            if game_state.current_player_id == game_state.human_player_id:
                print(f"\n轮到您出牌了!")

    def get_player_entity_by_id(self, player_id):
        """
        根据玩家ID获取玩家实体。

        参数:
            player_id (int): 要查找的玩家ID

        返回:
            int: 玩家实体ID，如果未找到则返回None
        """
        for ent, player in esper.get_component(PlayerComponent):
            if player.player_id == player_id:
                return ent
        return None

    def get_player_name_by_id(self, player_id):
        """
        根据玩家ID获取玩家名称。

        参数:
            player_id (int): 要查找的玩家ID

        返回:
            str: 找到的玩家名称，如果未找到则返回默认名称
        """
        for _, player in esper.get_component(PlayerComponent):
            if player.player_id == player_id:
                return player.name
        return f"Player{player_id}"  # 默认名称

    def display_hand(self, player: PlayerComponent, hand: Hand):
        """
        显示玩家的手牌。

        如果手牌尚未排序，会先对手牌进行排序，然后每行最多显示10张牌。

        参数:
            player (PlayerComponent): 玩家组件
            hand (Hand): 手牌组件
        """
        print(f"\n{player.name} 的手牌:")

        # 对手牌进行排序，便于阅读（如果尚未排序）
        if not hand.sorted:
            hand.cards = sorted(hand.cards, key=lambda card: (
                0 if card.rank == Rank.RED_JOKER else
                1 if card.rank == Rank.BLACK_JOKER else 2,
                list(Rank).index(
                    card.rank) if card.rank != Rank.RED_JOKER and card.rank != Rank.BLACK_JOKER else 0
            ))
            hand.sorted = True

        # 只显示牌面值
        cards = [card.get_rank_display() for card in hand.cards]
        cards_per_row = 10

        for i in range(0, len(cards), cards_per_row):
            row_cards = cards[i:i+cards_per_row]
            print(" ".join(row_cards))
        print()

    def player_play_card(self, player: PlayerComponent, hand: Hand, team: TeamComponent):
        """
        处理人类玩家的出牌操作。

        允许玩家通过控制台输入选择要打出的牌，支持以下格式：
        - 单张牌: "A", "2", "大王"等
        - 连续相同牌: "QQ", "333"等
        - 空格分隔相同牌: "5 5", "8 8 8"等

        当使用空格分隔格式时，会从手牌中随机选择指定数量的该牌面值的牌。

        参数:
            player (PlayerComponent): 玩家组件
            hand (Hand): 手牌组件
            team (TeamComponent): 队伍组件
        """
        while True:
            try:
                # 获取用户输入的牌面值
                card_input = input("请输入要出的牌 (例如: Q、QQ、5 5、RJ): ").strip()
                if not card_input:
                    print("输入为空，请重新输入。")
                    continue

                # 计算手牌中每种牌面值的数量
                card_counts = self.count_cards_by_rank(hand.cards)

                # 检查是否为空格分隔的相同牌 (如 "5 5" 或 "8 8 8")
                if " " in card_input:
                    parts = card_input.split()

                    # 验证所有部分是否相同
                    if len(set(parts)) == 1:
                        rank_value = parts[0]
                        count = len(parts)

                        # 检查玩家是否有足够的牌
                        if rank_value in card_counts and card_counts[rank_value] >= count:
                            # 随机选择指定数量的牌
                            candidates = [
                                card for card in hand.cards if card.get_rank_display() == rank_value]
                            played_cards = random.sample(candidates, count)
                        else:
                            print(f"您没有{count}张{rank_value}牌。")
                            continue
                    else:
                        print("输入格式错误，请确保所有牌都相同。")
                        continue

                # 判断输入是连续相同牌还是单张牌
                elif len(set(card_input)) == 1 and len(card_input) > 1:
                    # 连续相同牌，例如"QQ"
                    rank_value = card_input[0]
                    count = len(card_input)

                    # 对大小王做特殊处理
                    if rank_value == "大" and "大王" in card_counts and card_counts["大王"] >= count:
                        played_cards = self.find_cards_by_rank(
                            hand.cards, "大王", count)
                    elif rank_value == "小" and "小王" in card_counts and card_counts["小王"] >= count:
                        played_cards = self.find_cards_by_rank(
                            hand.cards, "小王", count)
                    # 常规牌
                    elif rank_value in card_counts and card_counts[rank_value] >= count:
                        played_cards = self.find_cards_by_rank(
                            hand.cards, rank_value, count)
                    else:
                        print(f"您没有{count}张{rank_value}牌。")
                        continue
                else:
                    # 处理单张牌或特殊输入(RJ/BJ)
                    if card_input == "RJ" and "RJ" in card_counts:
                        played_cards = self.find_cards_by_rank(
                            hand.cards, "RJ", 1)
                    elif card_input == "BJ" and "BJ" in card_counts:
                        played_cards = self.find_cards_by_rank(
                            hand.cards, "BJ", 1)
                    elif len(card_input) == 1 and card_input in card_counts:
                        played_cards = self.find_cards_by_rank(
                            hand.cards, card_input, 1)
                    elif card_input in card_counts:  # 处理两字符输入 (如"10")
                        played_cards = self.find_cards_by_rank(
                            hand.cards, card_input, 1)
                    else:
                        print(f"您没有这样的牌：{card_input}")
                        continue

                # 从手牌中移除打出的牌
                for card in played_cards:
                    hand.cards.remove(card)

                # 显示打出的牌
                if len(played_cards) == 1:
                    print(
                        f"{player.name} ({team.team.name}队) 打出了: {played_cards[0]}")
                else:
                    ranks = [card.get_rank_display() for card in played_cards]
                    print(
                        f"{player.name} ({team.team.name}队) 打出了: {' '.join(ranks)}")
                break

            except ValueError:
                print("无效的输入，请重试。")
            except KeyboardInterrupt:
                print("\n游戏中断")
                return

    def count_cards_by_rank(self, cards: List[Card]) -> Dict[str, int]:
        """
        统计手牌中每种牌面值的数量。

        参数:
            cards (List[Card]): 要统计的牌列表

        返回:
            Dict[str, int]: 牌面值到数量的映射字典
        """
        counts = defaultdict(int)
        for card in cards:
            rank = card.get_rank_display()
            counts[rank] += 1
        return counts

    def find_cards_by_rank(self, cards: List[Card], rank: str, count: int) -> List[Card]:
        """
        查找指定数量的特定牌面值的牌。

        参数:
            cards (List[Card]): 要查找的牌列表
            rank (str): 要查找的牌面值
            count (int): 要查找的牌的数量

        返回:
            List[Card]: 找到的牌列表
        """
        result = []
        for card in cards:
            if card.get_rank_display() == rank and len(result) < count:
                result.append(card)
        return result

    def find_next_player_with_cards(self, game_state):
        """
        查找下一个有牌的玩家ID。

        从当前玩家开始，按顺序查找下一个还有牌的玩家。
        如果所有玩家都没牌了，游戏应该已经结束。

        参数:
            game_state (GameStateComponent): 当前游戏状态

        返回:
            int: 下一个有牌的玩家ID
        """
        next_id = (game_state.current_player_id + 1) % 6

        # 如果已经有5个玩家出完牌，游戏应该结束
        if len(game_state.players_without_cards) >= 5:
            # 找出最后一个有牌的玩家
            for i in range(6):
                if i not in game_state.players_without_cards:
                    return i
            return next_id  # 以防万一

        # 循环查找直到找到一个有牌的玩家
        while next_id in game_state.players_without_cards:
            next_id = (next_id + 1) % 6

        return next_id
