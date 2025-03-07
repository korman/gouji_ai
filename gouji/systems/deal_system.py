import esper
import random
from typing import List, Dict
from ..components.card_components import Card, Hand
from ..components.game_components import GameStateComponent
from ..components.player_components import PlayerComponent
from .deck_system import DeckSystem
from ..constants import Rank


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
