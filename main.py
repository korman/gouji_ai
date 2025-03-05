import esper
import random
from enum import Enum, auto
from typing import List, Tuple

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


class Hand:
    def __init__(self):
        self.cards: List[Card] = []


class PlayerComponent:
    def __init__(self, name: str, is_ai: bool = False):
        self.name = name
        self.is_ai = is_ai


class TeamComponent:
    def __init__(self, team: Team):
        self.team = team


class GameStateComponent:
    def __init__(self):
        self.current_player = 0
        self.phase = "dealing"  # "dealing" 或 "playing"

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

            # 发牌完成后切换到出牌阶段
            for _, game_state in esper.get_component(GameStateComponent):
                game_state.phase = "playing"
                game_state.current_player = random.randint(0, 5)
                print(f"\n发牌完成! Player{game_state.current_player} 开始出牌\n")

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

        print(f"# 每个玩家获得相同数量的牌")
        print(f"cards_per_player = {cards_per_player}  # 4副牌(216张)÷6名玩家=36张/人")

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
                current_player = game_state.current_player

                # 找到当前玩家
                for player_ent, (player, hand, team) in esper.get_components(PlayerComponent, Hand, TeamComponent):
                    if player_ent == current_player:
                        if hand.cards:
                            if player.is_ai:
                                # AI随机出牌
                                card_index = random.randint(
                                    0, len(hand.cards) - 1)
                                played_card = hand.cards.pop(card_index)
                                print(
                                    f"{player.name} ({team.team.name}队) 打出了: {played_card}")
                            else:
                                # 玩家手动出牌
                                self.display_hand(player, hand)
                                self.player_play_card(player, hand, team)
                        else:
                            print(f"{player.name} 没有牌了!")

                        # 更新下一个玩家
                        game_state.current_player = (current_player + 1) % 6
                        break

    def display_hand(self, player: PlayerComponent, hand: Hand):
        print(f"\n{player.name} 的手牌:")
        cards_per_row = 10
        for i in range(0, len(hand.cards), cards_per_row):
            row_cards = hand.cards[i:i+cards_per_row]
            indices = [f"{j:2d}" for j in range(i, i+len(row_cards))]
            cards = [f"{card}" for card in row_cards]

            print(" ".join(indices))
            print(" ".join(cards))
        print()

    def player_play_card(self, player: PlayerComponent, hand: Hand, team: TeamComponent):
        while True:
            try:
                idx = int(input(f"请选择要出的牌 (0-{len(hand.cards) - 1}): "))
                if 0 <= idx < len(hand.cards):
                    played_card = hand.cards.pop(idx)
                    print(f"{player.name} ({team.team.name}队) 打出了: {played_card}")
                    break
                else:
                    print("无效的牌索引，请重试。")
            except ValueError:
                print("请输入有效的数字。")
            except KeyboardInterrupt:
                print("\n游戏中断")
                return

# 游戏初始化和运行


class GoujiGame:
    def __init__(self):
        # 初始化游戏系统
        self.deck_system = DeckSystem()
        self.deal_system = DealSystem(self.deck_system)
        self.play_system = PlaySystem()

        # 添加处理器
        esper.add_processor(self.deck_system)
        esper.add_processor(self.deal_system)
        esper.add_processor(self.play_system)

        # 创建游戏状态
        game_state_entity = esper.create_entity()
        esper.add_component(game_state_entity, GameStateComponent())

        # 创建玩家
        self.create_players()

    def create_players(self):
        # 创建6个玩家，交替分配队伍
        for i in range(6):
            player_entity = esper.create_entity()

            # 配置是否为AI (假设0号玩家是人类)
            is_ai = (i != 0)
            name = f"Player{i}" if is_ai else "玩家"

            esper.add_component(player_entity, PlayerComponent(name, is_ai))
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
