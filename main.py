import esper
import random
from enum import Enum, auto
from typing import List, Tuple, Dict
from collections import defaultdict

# 定义扑克牌的花色和点数


class Suit(Enum):
    HEART = "♥"
    DIAMOND = "♦"
    CLUB = "♣"
    SPADE = "♠"
    JOKER = "🃏"  # 添加王牌花色


class Rank(Enum):
    ACE = "A"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    RED_JOKER = "大王"    # 大王
    BLACK_JOKER = "小王"  # 小王


class Team(Enum):
    A = auto()
    B = auto()

# 组件定义


class Card:
    def __init__(self, suit: Suit, rank: Rank, deck_id: int):
        self.suit = suit
        self.rank = rank
        self.deck_id = deck_id

    def __str__(self):
        if self.rank in [Rank.RED_JOKER, Rank.BLACK_JOKER]:
            return self.rank.value
        return f"{self.suit.value}{self.rank.value}"

    def get_rank_display(self):
        """只返回牌的点数，用于简化显示"""
        if self.rank in [Rank.RED_JOKER, Rank.BLACK_JOKER]:
            return self.rank.value
        return self.rank.value


class Hand:
    def __init__(self):
        self.cards: List[Card] = []
        self.sorted: bool = False  # 添加标记表示是否已排序


class PlayerComponent:
    def __init__(self, name: str, player_id: int, is_ai: bool = False):
        self.name = name
        self.player_id = player_id  # 添加player_id来跟踪玩家ID
        self.is_ai = is_ai


class TeamComponent:
    def __init__(self, team: Team):
        self.team = team


class GameStateComponent:
    def __init__(self):
        self.current_player_id = 0  # 当前玩家的ID（不是实体ID）
        self.phase = "dealing"  # "dealing" 或 "playing"
        self.human_player_id = 0  # 记录人类玩家的ID

# 系统定义


class DeckSystem(esper.Processor):
    def __init__(self):
        self.deck: List[Card] = []
        self.initialized = False

    def process(self):
        if not self.initialized:
            self.create_deck()
            self.shuffle_deck()
            self.initialized = True

    def create_deck(self):
        # 创建4副牌 (包含大小王)
        for deck_id in range(4):
            # 常规牌
            for suit in [Suit.HEART, Suit.DIAMOND, Suit.CLUB, Suit.SPADE]:
                for rank in [r for r in Rank if r != Rank.RED_JOKER and r != Rank.BLACK_JOKER]:
                    self.deck.append(Card(suit, rank, deck_id))

            # 添加大小王
            self.deck.append(Card(Suit.JOKER, Rank.RED_JOKER, deck_id))
            self.deck.append(Card(Suit.JOKER, Rank.BLACK_JOKER, deck_id))

        print(f"创建了 {len(self.deck)} 张牌")

    def shuffle_deck(self):
        random.shuffle(self.deck)


class DealSystem(esper.Processor):
    def __init__(self, deck_system: DeckSystem):
        self.deck_system = deck_system
        self.dealt = False

    def process(self):
        # 只在第一次运行时发牌
        if not self.dealt:
            self.deal_all_cards()
            self.dealt = True

            # 发牌完成后，先展示人类玩家的手牌
            self.display_human_player_cards()

            # 发牌完成后切换到出牌阶段
            for _, game_state in esper.get_component(GameStateComponent):
                game_state.phase = "playing"
                game_state.current_player_id = random.randint(0, 5)

                # 找到开始玩家的名称
                player_name = self.get_player_name_by_id(
                    game_state.current_player_id)
                print(f"\n发牌完成! {player_name} 开始出牌\n")

                # 如果第一个出牌的不是人类玩家，提示等待
                if game_state.current_player_id != game_state.human_player_id:
                    print(f"等待 {player_name} 出牌...")

    def display_human_player_cards(self):
        """在游戏开始时就显示人类玩家的手牌"""
        for _, game_state in esper.get_component(GameStateComponent):
            human_player_id = game_state.human_player_id
            human_entity = self.get_player_entity_by_id(human_player_id)

            if human_entity is not None:
                player = esper.component_for_entity(
                    human_entity, PlayerComponent)
                hand = esper.component_for_entity(human_entity, Hand)

                print("\n您的初始手牌:")
                self.sort_and_display_hand(player, hand)

    def sort_and_display_hand(self, player: PlayerComponent, hand: Hand):
        """对手牌进行排序并显示"""
        # 对手牌进行排序，便于阅读
        sorted_cards = sorted(hand.cards, key=lambda card: (
            0 if card.rank == Rank.RED_JOKER else
            1 if card.rank == Rank.BLACK_JOKER else 2,
            list(Rank).index(
                card.rank) if card.rank != Rank.RED_JOKER and card.rank != Rank.BLACK_JOKER else 0
        ))

        # 只显示牌面值
        cards = [card.get_rank_display() for card in sorted_cards]
        cards_per_row = 10

        for i in range(0, len(cards), cards_per_row):
            row_cards = cards[i:i+cards_per_row]
            print(" ".join(row_cards))
        print()

        # 更新手牌以保持排序状态
        hand.cards = sorted_cards
        hand.sorted = True

    def get_player_name_by_id(self, player_id):
        """根据玩家ID获取玩家名称"""
        for _, player in esper.get_component(PlayerComponent):
            if player.player_id == player_id:
                return player.name
        return f"Player{player_id}"  # 默认名称

    def get_player_entity_by_id(self, player_id):
        """根据玩家ID获取玩家实体"""
        for ent, player in esper.get_component(PlayerComponent):
            if player.player_id == player_id:
                return ent
        return None

    def deal_all_cards(self):
        # 获取所有玩家
        players = []
        for ent, (player, hand) in esper.get_components(PlayerComponent, Hand):
            players.append((ent, player, hand))

        # 确保有6个玩家
        if len(players) != 6:
            print(f"错误: 需要6个玩家，但找到了{len(players)}个")
            return

        # 计算每个玩家应得的牌数
        total_cards = len(self.deck_system.deck)
        cards_per_player = total_cards // 6  # 应该是36张

        print(f"每位玩家获得 {cards_per_player} 张牌")

        # 为每个玩家分配牌
        for i, (ent, player, hand) in enumerate(players):
            start_idx = i * cards_per_player
            end_idx = start_idx + cards_per_player

            # 确保不超出范围
            if end_idx <= len(self.deck_system.deck):
                hand.cards = self.deck_system.deck[start_idx:end_idx]
                print(f"{player.name} 获得了 {len(hand.cards)} 张牌")
            else:
                print(f"警告: 牌不够分配给 {player.name}")

        # 清空牌组
        self.deck_system.deck = []


class PlaySystem(esper.Processor):
    def process(self):
        # 只有在出牌阶段才处理
        for _, game_state in esper.get_component(GameStateComponent):
            if game_state.phase == "playing":
                # 轮到人类玩家，显示手牌
                if game_state.current_player_id == game_state.human_player_id:
                    self.handle_human_turn(game_state)
                else:
                    # AI玩家出牌
                    self.handle_ai_turn(game_state)

    def handle_human_turn(self, game_state):
        """处理人类玩家回合"""
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
            else:
                print(f"\n{player.name} 没有牌了!")

            # 更新下一个玩家
            game_state.current_player_id = (
                game_state.current_player_id + 1) % 6

            # 提示等待下一个AI玩家
            next_player_name = self.get_player_name_by_id(
                game_state.current_player_id)
            print(f"\n等待 {next_player_name} 出牌...")

    def handle_ai_turn(self, game_state):
        """处理AI玩家回合"""
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
            else:
                print(f"\n{player.name} 没有牌了!")

            # 更新下一个玩家
            game_state.current_player_id = (
                game_state.current_player_id + 1) % 6

            # 如果下一个玩家是人类，提示并显示手牌
            if game_state.current_player_id == game_state.human_player_id:
                print(f"\n轮到您出牌了!")

    def get_player_entity_by_id(self, player_id):
        """根据玩家ID获取玩家实体"""
        for ent, player in esper.get_component(PlayerComponent):
            if player.player_id == player_id:
                return ent
        return None

    def get_player_name_by_id(self, player_id):
        """根据玩家ID获取玩家名称"""
        for _, player in esper.get_component(PlayerComponent):
            if player.player_id == player_id:
                return player.name
        return f"Player{player_id}"  # 默认名称

    def display_hand(self, player: PlayerComponent, hand: Hand):
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
        while True:
            try:
                # 获取用户输入的牌面值
                card_input = input("请输入要出的牌 (例如: Q 或 QQ 或 大王): ").strip()
                if not card_input:
                    print("输入为空，请重新输入。")
                    continue

                # 计算手牌中每种牌面值的数量
                card_counts = self.count_cards_by_rank(hand.cards)

                # 判断输入是多张相同牌还是单张牌
                if len(set(card_input)) == 1 and len(card_input) > 1:
                    # 多张相同牌，例如"QQ"
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
                    # 处理单张牌或特殊输入(大王/小王)
                    if card_input == "大王" and "大王" in card_counts:
                        played_cards = self.find_cards_by_rank(
                            hand.cards, "大王", 1)
                    elif card_input == "小王" and "小王" in card_counts:
                        played_cards = self.find_cards_by_rank(
                            hand.cards, "小王", 1)
                    elif len(card_input) == 1 and card_input in card_counts:
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
        """统计手牌中每种牌面值的数量"""
        counts = defaultdict(int)
        for card in cards:
            rank = card.get_rank_display()
            counts[rank] += 1
        return counts

    def find_cards_by_rank(self, cards: List[Card], rank: str, count: int) -> List[Card]:
        """查找指定数量的特定牌面值的牌"""
        result = []
        for card in cards:
            if card.get_rank_display() == rank and len(result) < count:
                result.append(card)
        return result

# 游戏初始化和运行


class GoujiGame:
    def __init__(self):
        # 重置esper世界状态（防止重复运行时的问题）
        esper.clear_database()

        # 创建游戏状态
        game_state_entity = esper.create_entity()
        esper.add_component(game_state_entity, GameStateComponent())

        # 创建玩家
        self.create_players()

        # 初始化游戏系统
        self.deck_system = DeckSystem()
        self.deal_system = DealSystem(self.deck_system)
        self.play_system = PlaySystem()

        # 添加处理器
        esper.add_processor(self.deck_system)
        esper.add_processor(self.deal_system)
        esper.add_processor(self.play_system)

    def create_players(self):
        # 创建6个玩家，交替分配队伍
        for i in range(6):
            player_entity = esper.create_entity()

            # 配置是否为AI (假设0号玩家是人类)
            is_ai = (i != 0)
            name = f"玩家" if i == 0 else f"Player{i}"

            esper.add_component(player_entity, PlayerComponent(name, i, is_ai))
            esper.add_component(player_entity, Hand())

            # 交替分配队伍 (0,2,4为A队；1,3,5为B队)
            team = Team.A if i % 2 == 0 else Team.B
            esper.add_component(player_entity, TeamComponent(team))

    def run(self):
        print("够级游戏开始！")

        # 游戏主循环
        esper.process()  # 处理发牌

        while True:
            try:
                esper.process()  # 处理出牌
                input_text = input("按Enter继续，输入q退出: ")
                if input_text.lower() == 'q':
                    break
            except KeyboardInterrupt:
                break


if __name__ == "__main__":
    game = GoujiGame()
    game.run()
