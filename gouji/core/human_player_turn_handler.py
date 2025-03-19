import sys
import esper
import random
from ..components import Card
from ..interface import TurnHandlerInterface
from ..interface import PlayerAction
from typing import List, Tuple
from ..components import PlayerComponent, Hand, TeamComponent, GameStateComponent
from ..systems import DeckSystem, DealSystem, PlaySystem
from ..utils import CardPatternChecker


class HumanPlayerTurnHandler(TurnHandlerInterface):
    """
    人类玩家回合处理器，允许用户通过命令行交互方式出牌
    """

    def handle_player_turn(
        self, game_state, player_id, play_system
    ) -> Tuple[PlayerAction, List[Card]]:
        """
        处理人类玩家的回合，提供交互式界面

        参数:
            game_state: 游戏状态组件
            player_id: 当前玩家ID
            play_system: 出牌系统的引用
        """
        human_entity = play_system.get_player_entity_by_id(player_id)

        if human_entity is not None:
            player = esper.component_for_entity(human_entity, PlayerComponent)
            hand = esper.component_for_entity(human_entity, Hand)
            team = esper.component_for_entity(human_entity, TeamComponent)

            play_system.display_hand(player, hand)

            while True:
                try:
                    # 获取用户输入的牌面值

                    card_input = None

                    # 当前玩家是最后一个有效出牌的玩家时，card_input的内容中没有pass
                    if (
                        game_state.current_player_id
                        == play_system.get_last_effective_player_id()
                    ):
                        card_input = input(
                            "请输入要出的牌 (例如: Q、Q Q、5 5、RJ，或输入 'exit' 退出游戏: "
                        ).strip()
                    else:
                        card_input = input(
                            "请输入要出的牌 (例如: Q、Q Q、5 5、RJ，或输入 'p' 表示PASS),'exit' 退出游戏: "
                        ).strip()

                    # 处理空输入
                    if not card_input:
                        print("输入为空，请重新输入。")
                        continue

                    # 判断输入是否是exit，如果是则用退出游戏
                    if card_input.lower() == "exit":
                        print("游戏结束")
                        sys.exit()
                        return

                    # 处理PASS逻辑
                    if card_input.lower() == "p":
                        return PlayerAction.PASS, []
                        # 如果当前玩家是最后一个有效出牌的玩家，不允许pass
                        # if (
                        #     game_state.current_player_id
                        #     == self.last_effective_player_id
                        # ):
                        #     print("您不能选择PASS，因为您是最后一个有效出牌的玩家。")
                        #     continue

                    # 计算手牌中每种牌面值的数量
                    card_counts = play_system.count_cards_by_rank(hand.cards)

                    # 处理不同的出牌输入情况
                    if " " in card_input:
                        # 处理空格分隔的相同牌
                        parts = card_input.split()
                        if len(set(parts)) == 1:
                            rank_value = parts[0]
                            count = len(parts)
                            if (
                                rank_value in card_counts
                                and card_counts[rank_value] >= count
                            ):
                                # 随机选择指定数量的牌
                                candidates = [
                                    card
                                    for card in hand.cards
                                    if card.get_rank_display() == rank_value
                                ]
                                current_played_cards = random.sample(
                                    candidates, count)
                            else:
                                print(f"您没有{count}张{rank_value}牌。")
                                continue
                        else:
                            print("输入格式错误，请确保所有牌都相同。")
                            continue

                    elif len(set(card_input)) == 1 and len(card_input) > 1:
                        # 处理连续相同牌，例如"QQ"
                        rank_value = card_input[0]
                        count = len(card_input)

                        # 对大小王做特殊处理
                        if (
                            rank_value == "大"
                            and "大王" in card_counts
                            and card_counts["大王"] >= count
                        ):
                            current_played_cards = self.find_cards_by_rank(
                                hand.cards, "大王", count
                            )
                        elif (
                            rank_value == "小"
                            and "小王" in card_counts
                            and card_counts["小王"] >= count
                        ):
                            current_played_cards = self.find_cards_by_rank(
                                hand.cards, "小王", count
                            )
                        # 常规牌
                        elif (
                            rank_value in card_counts
                            and card_counts[rank_value] >= count
                        ):
                            current_played_cards = self.find_cards_by_rank(
                                hand.cards, rank_value, count
                            )
                        else:
                            print(f"您没有{count}张{rank_value}牌。")
                            continue

                    else:
                        # 处理单张牌或特殊输入(RJ/BJ)
                        if card_input in ["RJ", "BJ"] and card_input in card_counts:
                            current_played_cards = play_system.find_cards_by_rank(
                                hand.cards, card_input, 1
                            )
                        elif len(card_input) in [1, 2] and card_input in card_counts:
                            current_played_cards = play_system.find_cards_by_rank(
                                hand.cards, card_input, 1
                            )
                        else:
                            print(f"您没有这样的牌：{card_input}")
                            continue

                    # 验证出牌是否合法（是否能大过上一手牌）
                    if (
                        hasattr(self, "last_played_cards")
                        and play_system.get_last_played_cards() is not None
                    ):
                        if not CardPatternChecker.can_beat(
                            current_played_cards, self.last_played_cards
                        ):
                            print("您出的牌不能大过上一手牌，请重新选择。")
                            continue

                    # 返回current_played_cards与出牌枚举
                    return PlayerAction.PLAY, current_played_cards

                except ValueError:
                    print("无效的输入，请重试。")
                except KeyboardInterrupt:
                    print("\n游戏中断")
                    return
