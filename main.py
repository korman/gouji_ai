import esper
import random
from enum import Enum, auto
from typing import List, Tuple, Dict
from collections import defaultdict

# 定义扑克牌的花色和点数


class Suit(Enum):
    """
    扑克牌花色枚举。

    表示扑克牌的四种基本花色以及王牌的特殊花色。
    使用Unicode字符作为花色的图形表示。

    属性:
        HEART (str): 红桃 ♥
        DIAMOND (str): 方块 ♦
        CLUB (str): 梅花 ♣
        SPADE (str): 黑桃 ♠
        JOKER (str): 王牌 🃏
    """
    HEART = "♥"
    DIAMOND = "♦"
    CLUB = "♣"
    SPADE = "♠"
    JOKER = "🃏"  # 添加王牌花色


class Rank(Enum):
    """
    扑克牌点数枚举。

    表示扑克牌的所有可能点数，包括A到K的常规牌以及大小王。

    属性:
        ACE (str): A
        TWO (str) 到 KING (str): 2-K的常规点数
        RED_JOKER (str): 大王
        BLACK_JOKER (str): 小王
    """
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
    """
    队伍枚举。

    表示够级游戏中的两个队伍。
    使用auto()自动分配枚举值。

    属性:
        A: A队
        B: B队
    """
    A = auto()
    B = auto()


# 组件定义

class Card:
    """
    扑克牌类。

    表示够级游戏中的一张扑克牌，包含花色、点数和所属牌组的ID。

    属性:
        suit (Suit): 牌的花色
        rank (Rank): 牌的点数
        deck_id (int): 所属牌组的ID（用于区分多副牌）

    方法:
        __str__(): 返回牌的字符串表示，例如"♥A"或"大王"
        get_rank_display(): 仅返回牌的点数值，用于简化显示
    """

    def __init__(self, suit: Suit, rank: Rank, deck_id: int):
        """
        初始化一张扑克牌。

        参数:
            suit (Suit): 牌的花色
            rank (Rank): 牌的点数
            deck_id (int): 所属牌组的ID
        """
        self.suit = suit
        self.rank = rank
        self.deck_id = deck_id

    def __str__(self):
        """
        返回牌的字符串表示。

        对于大小王只返回其名称，对于常规牌返回花色加点数。

        返回:
            str: 牌的字符串表示，例如"♥A"或"大王"
        """
        if self.rank in [Rank.RED_JOKER, Rank.BLACK_JOKER]:
            return self.rank.value
        return f"{self.suit.value}{self.rank.value}"

    def get_rank_display(self):
        """
        获取牌面的显示值

        返回:
            str: 便于显示的牌面值表示
        """
        if self.rank == Rank.RED_JOKER:
            return "RJ"  # 改为"RJ"代替"大王"
        elif self.rank == Rank.BLACK_JOKER:
            return "BJ"  # 改为"BJ"代替"小王"
        elif self.rank == Rank.ACE:
            return "A"
        elif self.rank == Rank.JACK:
            return "J"
        elif self.rank == Rank.QUEEN:
            return "Q"
        elif self.rank == Rank.KING:
            return "K"
        else:
            # 对于数字牌，直接返回数值的字符串
            return str(self.rank.value)


class Hand:
    """
    玩家手牌类。

    表示一个玩家持有的所有牌。

    属性:
        cards (List[Card]): 玩家持有的牌列表
        sorted (bool): 标记手牌是否已经排序
    """

    def __init__(self):
        """
        初始化一个空的手牌。
        """
        self.cards: List[Card] = []
        self.sorted: bool = False  # 添加标记表示是否已排序


class PlayerComponent:
    """
    玩家组件。

    表示游戏中的一个玩家，是ECS架构中的组件。

    属性:
        name (str): 玩家名称
        player_id (int): 玩家ID，用于在游戏逻辑中标识玩家
        is_ai (bool): 标记该玩家是否为AI控制
    """

    def __init__(self, name: str, player_id: int, is_ai: bool = False):
        """
        初始化玩家组件。

        参数:
            name (str): 玩家名称
            player_id (int): 玩家的唯一ID
            is_ai (bool, 可选): 是否为AI玩家，默认为False
        """
        self.name = name
        self.player_id = player_id  # 添加player_id来跟踪玩家ID
        self.is_ai = is_ai


class TeamComponent:
    """
    队伍组件。

    表示玩家所属的队伍，是ECS架构中的组件。
    在够级游戏中，玩家被分为A队和B队。

    属性:
        team (Team): 玩家所属的队伍
    """

    def __init__(self, team: Team):
        """
        初始化队伍组件。

        参数:
            team (Team): 玩家所属的队伍(A或B)
        """
        self.team = team


class GameStateComponent:
    """
    游戏状态组件。

    管理游戏的全局状态，是ECS架构中的组件。

    属性:
        current_player_id (int): 当前正在行动的玩家ID
        phase (str): 游戏当前阶段，可以是"dealing"(发牌阶段)或"playing"(出牌阶段)
        human_player_id (int): 人类玩家的ID，默认为0
    """

    def __init__(self):
        """
        初始化游戏状态组件，设置默认状态。
        """
        self.phase = "dealing"  # 游戏阶段：dealing(发牌), playing(出牌), game_over(结束)
        self.current_player_id = 0  # 当前玩家ID
        self.human_player_id = 0  # 人类玩家ID (默认为0)
        self.players_without_cards = set()  # 新增：记录已经出完牌的玩家ID
        self.rankings = []  # 新增：记录玩家完成顺序

# 系统定义


class DeckSystem(esper.Processor):
    """
    牌组系统处理器，负责创建和管理游戏中使用的卡牌。

    继承自esper.Processor，作为ECS架构中的处理器组件。
    该系统创建四副完整的扑克牌（每副包含52张常规牌和2张王牌），
    并提供洗牌功能。

    属性:
        deck (List[Card]): 存储所有卡牌的列表
        initialized (bool): 标记牌组是否已初始化的标志
    """

    def __init__(self):
        """
        初始化DeckSystem实例。

        创建一个空牌组并将初始化状态设置为False。
        """
        self.deck: List[Card] = []
        self.initialized = False

    def process(self):
        """
        处理器的主要执行方法，由ECS系统自动调用。

        如果牌组尚未初始化，则创建牌组并洗牌，然后将初始化状态设置为True。
        这确保牌组仅被初始化一次。
        """
        if not self.initialized:
            self.create_deck()
            self.shuffle_deck()
            self.initialized = True

    def create_deck(self):
        """
        创建完整的牌组。

        生成4副完整的扑克牌，每副包含：
        - 52张常规牌（4种花色 × 13种点数）
        - 2张王牌（大王和小王）

        总共创建216张牌，并在控制台输出创建的牌数。
        """
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
        """
        对牌组进行随机洗牌。

        使用Python的random.shuffle函数打乱deck列表中牌的顺序。
        """
        random.shuffle(self.deck)


class DealSystem(esper.Processor):
    """
    发牌系统处理器，负责游戏中的发牌流程和初始化游戏状态。

    继承自esper.Processor，作为ECS架构中的处理器组件。
    该系统在游戏开始时将牌组中的牌均匀分配给所有玩家，
    并设置初始游戏状态，确定第一个出牌的玩家。

    属性:
        deck_system (DeckSystem): 牌组系统的引用，用于获取要分发的牌组
        dealt (bool): 标记牌是否已经发放的标志
    """

    def __init__(self, deck_system: DeckSystem):
        """
        初始化DealSystem实例。

        参数:
            deck_system (DeckSystem): 牌组系统实例，提供要发放的牌组
        """
        self.deck_system = deck_system
        self.dealt = False

    def process(self):
        """
        处理器的主要执行方法，由ECS系统自动调用。

        只在第一次运行时执行发牌操作，发牌完成后：
        1. 显示人类玩家的手牌
        2. 将游戏阶段切换到"playing"(出牌阶段)
        3. 随机选择第一个出牌的玩家
        4. 显示相应的游戏状态信息
        """
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
        """
        在游戏开始时显示人类玩家的手牌。

        查找人类玩家实体，获取其手牌组件，并调用sort_and_display_hand
        方法对手牌进行排序和显示。
        """
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
        """
        对手牌进行排序并显示。

        排序规则：
        1. 大王优先（最高）
        2. 小王次之
        3. 其他牌按点数排序

        排序后的手牌每行显示最多10张，并更新手牌组件中的牌序。

        参数:
            player (PlayerComponent): 玩家组件
            hand (Hand): 手牌组件
        """
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

    def deal_all_cards(self):
        """
        将牌组中的所有牌均匀分配给所有玩家。

        过程:
        1. 获取所有具有PlayerComponent和Hand组件的玩家实体
        2. 确认玩家数量为6个
        3. 计算每个玩家应得的牌数
        4. 按顺序为每个玩家分配牌
        5. 清空牌组

        如果玩家数量不是6个或牌数不够分配，会打印警告信息。
        """
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

# 游戏初始化和运行


class GoujiGame:
    """
    够级游戏主类，负责初始化游戏环境、创建游戏组件及运行游戏。

    该类是游戏的核心控制器，使用ECS(实体组件系统)架构管理游戏:
    1. 初始化游戏状态和玩家
    2. 创建并注册游戏系统处理器
    3. 提供游戏主循环逻辑

    使用esper作为ECS框架来管理实体、组件和系统。
    """

    def __init__(self):
        """
        初始化游戏环境和组件。

        进行以下设置:
        1. 清空esper数据库，确保游戏状态干净
        2. 创建游戏状态实体和组件
        3. 创建游戏中的玩家实体
        4. 初始化游戏所需的各个系统处理器
        5. 将处理器添加到esper世界中
        """
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
        """
        创建游戏中的6个玩家实体。

        为每个玩家:
        1. 创建玩家实体
        2. 添加PlayerComponent组件(包含名称、ID和是否为AI)
        3. 添加Hand组件(用于存储手牌)
        4. 添加TeamComponent组件(分配队伍)

        玩家0设置为人类玩家，其余设置为AI玩家。
        玩家按偶数(0,2,4)分入A队，奇数(1,3,5)分入B队。
        """
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

                # 只有当轮到人类玩家时才显示提示
                if game_state.current_player_id == game_state.human_player_id:
                    input_text = input("按Enter继续，输入q退出: ")
                    if input_text.lower() == 'q':
                        break
                # AI回合自动继续，无需用户输入
                else:
                    # 可选：添加短暂延迟，让用户能看清AI的操作
                    # import time
                    # time.sleep(1)
                    pass

            except KeyboardInterrupt:
                break


if __name__ == "__main__":
    """
    游戏主入口点。

    创建GoujiGame实例并启动游戏。
    当程序作为脚本直接运行时执行此代码块。
    """
    game = GoujiGame()
    game.run()
