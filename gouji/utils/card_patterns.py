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

        new_ranks = [card.rank for card in cards]
        if not all(rank == new_ranks[0] for rank in new_ranks):
            return False

        return True

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
    def find_all_beating_combinations(
        hand_cards: List[Card], target_cards: List[Card] = None
    ) -> List[List[Card]]:
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
    def find_all_beating_combinations_without_splitting(
        hand_cards: List[Card], target_cards: List[Card] = None
    ) -> List[List[Card]]:
        """
        找出能大过目标牌的所有不拆牌组合

        不拆牌意味着只使用手牌中数量与目标牌相同的完整牌组，不拆分任何牌组。
        例如，如果手牌中有 4 4 4 4，目标牌是 3 3 3，则不能使用其中的 4 4 4（这属于拆牌）。

        参数:
            hand_cards: 手中的牌
            target_cards: 需要大过的目标牌组（可选）

        返回:
            所有能大过目标牌的不拆牌组合
        """
        # 当目标牌为空时，返回所有可能的合法出牌组合
        if target_cards is None or len(target_cards) == 0:
            return CardPatternChecker._find_all_valid_plays(hand_cards)

        # 获取目标牌的数量和点数
        target_count = len(target_cards)
        target_rank = target_cards[0].rank

        # 将手牌按点数分组
        rank_groups = {}
        for card in hand_cards:
            if card.rank not in rank_groups:
                rank_groups[card.rank] = []
            rank_groups[card.rank].append(card)

        beating_combinations = []

        # 遍历每种点数的牌组
        for rank, cards in rank_groups.items():
            # 只有当牌组中有与目标牌数量相同的牌，且点数更大时才是有效组合
            if len(cards) == target_count and rank.get_value() > target_rank.get_value():
                # 不拆牌原则：只取与目标牌数量相同的牌
                selected_cards = cards[:target_count]
                beating_combinations.append(selected_cards)

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

    @staticmethod
    def calculate_armor_reduction(armor, factor=0.06):
        """
        计算魔兽争霸3中护甲提供的伤害减免比例

        参数:
            armor (float): 护甲值
            factor: 系数，原公式为0.06，降低此值会使曲线更平缓

        返回:
            float: 伤害减免比例（0-1之间的值，代表减免的百分比）
        """
        return armor * factor / (1 + factor * armor)

    @staticmethod
    def calculate_breaking_cost(selected_cards: List[Card], hand: List[Card]) -> float:
        """
        计算出牌操作的拆牌代价

        参数:
            selected_cards: 要出的牌
            hand: 手中所有的牌

        返回:
            float: 拆牌代价(0-10)，0表示无拆牌，值越大代表拆牌风险越高
        """
        if not selected_cards or len(selected_cards) == 0:
            return 0.0

        # 获取选中牌的点数值
        selected_value = selected_cards[0].rank.get_value()

        # 将手牌按点数值分组
        value_groups = {}
        for card in hand:
            card_value = card.rank.get_value()
            if card_value not in value_groups:
                value_groups[card_value] = []
            value_groups[card_value].append(card)

        # 获取该点数值的所有牌
        same_value_cards = value_groups.get(selected_value, [])

        # 如果出牌数量等于该点数的总数量，则不是拆牌
        if len(selected_cards) == len(same_value_cards):
            return 0.0

        # 剩余的牌数
        remaining_count = len(same_value_cards) - len(selected_cards)

        # 基本代价计算 - 与牌值成反比
        # 牌值越大，拆牌代价越小（如2的get_value为15，拆牌代价小）
        # 牌值越小，拆牌代价越大（如3的get_value为3，拆牌代价大）
        max_value = 17  # 假设最大牌值（如大王）
        min_value = 3  # 假设最小牌值（如3）

        # 牌值系数: 值越小代价越高，值越大代价越低
        value_range = max_value - min_value
        value_factor = 1.0 - min(
            1.0, max(0.0, (selected_value - min_value) / value_range)
        )

        # 基础代价: 取决于剩余牌数和牌值
        base_cost = 0.0

        # 根据剩余牌数计算代价
        if remaining_count == 1:
            # 留下单张的代价
            base_cost = 5.0 * value_factor  # 小牌留单张代价高，大牌留单张代价低
        elif remaining_count == 2:
            # 留下两张的代价
            base_cost = 3.0 * value_factor
        elif remaining_count == 3:
            # 留下三张的代价
            base_cost = 1.5 * value_factor
        else:
            # 其他情况的基本代价
            base_cost = 1.0 * value_factor

        return base_cost

    @staticmethod
    def cards_to_pattern_string(cards: List[Card]) -> str:
        """
        将一组扑克牌转换为牌型字符串表示

        参数:
            cards: 要转换的扑克牌列表

        返回:
            str: 牌型的字符串表示，如[3 3 4 4]
        """
        if not cards:
            return "[]"

        # 提取每张牌的点数显示值
        ranks = [card.get_rank_display() for card in cards]

        # 对牌进行排序(可选，如果需要)
        # 这里可能需要自定义排序逻辑，因为显示值可能是字符串

        # 构建字符串表示
        ranks_str = " ".join(ranks)
        return f"[{ranks_str}]"

    @staticmethod
    def get_total_value(cards: List[Card]) -> int:
        """
        获取一组牌的点数总和

        参数:
            cards: 要计算总值的扑克牌列表

        返回:
            int: 所有牌的点数总和
        """
        if not cards:
            return 0

        total = 0
        for card in cards:
            total += card.rank.get_value()

        return total

    @staticmethod
    def get_value_difference(cards1: List[Card], cards2: List[Card]) -> int:
        """
        计算两组牌的牌值总和之差

        参数:
            cards1: 第一组扑克牌
            cards2: 第二组扑克牌

        返回:
            int: cards1总值减去cards2总值的差值
        """
        # 获取第一组牌的总值
        value1 = CardPatternChecker.get_total_value(cards1)

        # 获取第二组牌的总值
        value2 = CardPatternChecker.get_total_value(cards2)

        # 返回差值
        return value1 - value2
