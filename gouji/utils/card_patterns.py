from ..components import Card
from typing import List


class CardPatternChecker:
    """
    牌型检查工具类，负责处理所有与牌型相关的逻辑。
    包括牌型识别、合法性验证、牌型比较和可用组合提取。
    """

    @staticmethod
    def identify_pattern(cards):
        """识别一组牌的牌型"""
        # 实现牌型识别逻辑
        pass

    @staticmethod
    def is_valid_pattern(cards):
        """检查是否是有效的牌型组合"""
        # 实现牌型合法性检查
        pass

    @staticmethod
    def can_beat(new_cards: List[Card], previous_cards: List[Card] = None) -> bool:
        """
        检查新的一组牌是否能大过之前的牌

        规则：
        1. 如果previous_cards为空，任何牌组都可以出
        2. 牌数量必须相同
        3. 所有牌必须是同一点数
        4. 新牌的点数必须大于之前牌的点数

        参数:
            new_cards: 新打出的牌
            previous_cards: 之前打出的牌（可选）

        返回:
            bool: 是否能大过之前的牌
        """
        # 如果previous_cards为空，任何牌组都可以出
        if previous_cards is None or len(previous_cards) == 0:
            return True

        # 牌数必须相同
        if len(new_cards) != len(previous_cards):
            return False

        # 检查新牌是否都是同一点数
        new_ranks = [card.rank for card in new_cards]
        if not all(rank == new_ranks[0] for rank in new_ranks):
            return False

        # 检查前一手牌是否都是同一点数
        prev_ranks = [card.rank for card in previous_cards]
        if not all(rank == prev_ranks[0] for rank in prev_ranks):
            return False

        # 比较点数大小
        new_value = new_ranks[0].get_value()
        prev_value = prev_ranks[0].get_value()

        return new_value > prev_value

    @staticmethod
    def find_all_beating_combinations(hand_cards: List[Card], target_cards: List[Card] = None) -> List[List[Card]]:
        """
        找出能大过目标牌的所有组合

        参数:
            hand_cards: 手中的牌
            target_cards: 需要大过的目标牌组（可选）

        返回:
            所有能大过目标牌的牌组组合
        """
        # 当目标牌为空时，返回所有可能的合法出牌组合
        if target_cards is None or len(target_cards) == 0:
            return CardPatternChecker._find_all_valid_plays(hand_cards)

        # 将手牌按点数分组
        rank_groups = {}
        for card in hand_cards:
            if card.rank not in rank_groups:
                rank_groups[card.rank] = []
            rank_groups[card.rank].append(card)

        beating_combinations = []

        # 遍历每种点数的牌组
        for rank, cards in rank_groups.items():
            # 尝试不同数量的牌组合
            for count in range(1, len(cards) + 1):
                # 取当前数量的牌组
                current_combination = cards[:count]

                # 直接使用can_beat方法检查是否能大过目标牌
                if CardPatternChecker.can_beat(current_combination, target_cards):
                    beating_combinations.append(current_combination)

        return beating_combinations

    @staticmethod
    def _find_all_valid_plays(hand_cards: List[Card]) -> List[List[Card]]:
        """
        找出手牌中所有可能的合法出牌组合

        参数:
            hand_cards: 玩家手上的牌

        返回:
            所有可能的合法出牌组合
        """
        if not hand_cards:
            return []

        # 将手牌按点数分组
        rank_groups = {}
        for card in hand_cards:
            if card.rank not in rank_groups:
                rank_groups[card.rank] = []
            rank_groups[card.rank].append(card)

        all_valid_plays = []

        # 对每种点数的牌，生成1至n张的所有组合
        for rank, cards in rank_groups.items():
            for count in range(1, len(cards) + 1):
                all_valid_plays.append(cards[:count])

        return all_valid_plays
