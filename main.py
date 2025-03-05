import esper
import random
from enum import Enum, auto
from typing import List, Tuple
import sys

# 定义扑克牌的花色和点数


class Suit(Enum):
    HEART = "♥"
    DIAMOND = "♦"
    CLUB = "♣"
    SPADE = "♠"


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


class Team(Enum):
    A = auto()
    B = auto()

# 组件定义


class Card:
    def __init__(self, suit: Suit, rank: Rank, deck_id: int):
        self.suit = suit
        self.rank = rank
        self.deck_id = deck_id  # 标识是哪一副牌

    def __str__(self):
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


class TurnComponent:
    def __init__(self, current_player: int = 0):
        self.current_player = current_player
        self.is_dealing = True  # 是否在发牌阶段
        self.is_playing = False  # 是否在出牌阶段

# 系统定义


class DeckSystem(esper.Processor):
    def __init__(self):
        self.deck: List[Card] = []

    def process(self):
        # 只在初始化时执行一次
        if not self.deck:
            self.create_deck()
            self.shuffle_deck()

    def create_deck(self):
        # 创建4副牌 (不含大小王)
        for deck_id in range(4):
            for suit in Suit:
                for rank in Rank:
                    self.deck.append(Card(suit, rank, deck_id))

    def shuffle_deck(self):
        random.shuffle(self.deck)

    def draw_card(self) -> Card:
        if self.deck:
            return self.deck.pop()
        return None


class DealSystem(esper.Processor):
    def __init__(self, deck_system: DeckSystem):
        self.deck_system = deck_system

    def process(self):
        # 查找TurnComponent并检查是否在发牌阶段
        for ent, turn in esper.get_component(TurnComponent):
            if turn.is_dealing:
                # 检查是否还有牌可以发
                if self.deck_system.deck:
                    # 获取当前玩家
                    current_player = turn.current_player

                    # 给当前玩家发一张牌
                    for player_ent, (player, hand) in esper.get_components(PlayerComponent, Hand):
                        if player_ent == current_player:
                            card = self.deck_system.draw_card()
                            if card:
                                hand.cards.append(card)
                                print(f"{player.name} 抽到了: {card}")

                            # 更新下一个玩家
                            turn.current_player = (current_player + 1) % 6
                            break
                else:
                    # 所有牌发完，进入出牌阶段
                    turn.is_dealing = False
                    turn.is_playing = True
                    turn.current_player = random.randint(0, 5)  # 随机选择一个玩家开始出牌
                    print(f"发牌完成，随机选择 Player{turn.current_player} 开始出牌")


class PlaySystem(esper.Processor):
    def process(self):
        # 查找TurnComponent并检查是否在出牌阶段
        for ent, turn in esper.get_component(TurnComponent):
            if turn.is_playing:
                current_player = turn.current_player

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
                        turn.current_player = (current_player + 1) % 6
                        break

    def display_hand(self, player: PlayerComponent, hand: Hand):
        print(f"\n{player.name} 的手牌:")
        for i, card in enumerate(hand.cards):
            print(f"{i}: {card}", end=", " if (i + 1) % 10 != 0 else "\n")
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

# 游戏初始化和运行


class GoujiGame:
    def __init__(self):
        self.deck_system = DeckSystem()
        self.deal_system = DealSystem(self.deck_system)
        self.play_system = PlaySystem()

        # 添加处理器
        esper.add_processor(self.deck_system)
        esper.add_processor(self.deal_system)
        esper.add_processor(self.play_system)

        # 创建玩家
        self.create_players()

        # 创建回合控制
        turn_entity = esper.create_entity()
        # 随机选择一个玩家开始抽牌
        esper.add_component(turn_entity, TurnComponent(
            current_player=random.randint(0, 5)))

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

        # 初始牌组
        esper.process()

        # 游戏主循环
        while True:
            try:
                esper.process()
                # 简单延迟，避免输出太快
                if input("按Enter键继续，输入q退出: ").lower() == 'q':
                    break
            except KeyboardInterrupt:
                break


if __name__ == "__main__":
    game = GoujiGame()
    game.run()
