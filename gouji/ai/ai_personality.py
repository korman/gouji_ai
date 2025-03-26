# ai_personality.py
from enum import Enum
from dataclasses import dataclass

# 定义奖励映射（排名 -> 奖励值）
RANK_REWARDS = {
    0: 10.0,  # 第1名 +10
    1: 5.0,   # 第2名 +5
    2: 0.0,   # 第3名 0
    3: 0.0,   # 第4名 0
    4: -5.0,  # 第5名 -5
    5: -10.0  # 第6名 -10
}


@dataclass
class AIPersonalityConfig:
    """
    通用AI性格配置类，适用于不同类型的强化学习智能体
    (DQN, PPO, A2C, DDPG等)
    """

    name: str
    breaking_cost_factor: float = 0.001  # 拆牌惩罚系数
    risk_factor: float = 1.0  # 风险倾向系数
    play_reward_factor: float = 0.01  # 出牌奖励系数
    pass_penalty: float = 0.01  # PASS惩罚
    bomb_value: float = 1.0  # 炸弹价值系数
    early_lead_bonus: float = 0.0  # 提前出牌奖励
    small_card_priority: float = 0.0  # 小牌优先系数
    dynamic_adjustment: bool = False  # 是否根据局势动态调整策略
    team_cooperation_factor: float = 0.0  # 团队合作系数(辅助型AI专用)
    difference_penalty: float = 0.01  # 牌值差异惩罚系数

    # 添加PPO特定参数
    exploration_factor: float = 1.0  # 探索因子，影响PPO的熵正则化

    def get_algorithm_params(self, algorithm_type):
        """
        获取特定算法类型的参数配置
        允许为不同算法返回自定义参数

        参数:
            algorithm_type: 算法类型，如'dqn', 'ppo', 'a2c'等

        返回:
            dict: 算法特定参数
        """
        if algorithm_type.lower() == "dqn":
            return {
                "epsilon_decay": 0.998 * self.risk_factor,
                "epsilon_min": 0.01 / self.risk_factor,
            }
        elif algorithm_type.lower() == "ppo":
            return {
                "clip_param": 0.2 * self.risk_factor,
                "entropy_coef": 0.01 * self.exploration_factor,
                "vf_coef": 0.5,
            }
        # 可继续扩展其他算法
        return {}


class AIPersonality(Enum):
    """AI性格枚举，包含不同风格的AI预设"""

    # 平衡型AI - 默认性格，各方面较为均衡
    BALANCED = AIPersonalityConfig(
        name="平衡型",
        breaking_cost_factor=0.001,
        risk_factor=1.0,
        play_reward_factor=0.01,
        pass_penalty=0.01,
    )

    # 保守型AI - 极少拆牌，重视牌型完整性
    CONSERVATIVE = AIPersonalityConfig(
        name="保守型",
        breaking_cost_factor=0.01,  # 高拆牌惩罚
        risk_factor=0.5,  # 低风险偏好
        play_reward_factor=0.005,  # 减少出牌激励
        pass_penalty=0.05,  # 降低PASS惩罚
        bomb_value=1.5,  # 高炸弹价值
    )

    # 激进型AI - 优先快速出牌，敢于拆牌
    AGGRESSIVE = AIPersonalityConfig(
        name="激进型",
        breaking_cost_factor=0.05,  # 低拆牌惩罚
        risk_factor=1.5,  # 高风险偏好
        play_reward_factor=0.03,  # 高出牌奖励
        pass_penalty=0.2,  # 高PASS惩罚
        early_lead_bonus=0.02,  # 提前出牌额外奖励
    )

    # 策略型AI - 根据局势动态调整策略
    STRATEGIC = AIPersonalityConfig(
        name="策略型",
        breaking_cost_factor=0.12,
        risk_factor=1.0,
        play_reward_factor=0.015,
        pass_penalty=0.12,
        dynamic_adjustment=True,  # 启用动态策略调整
    )

    # 小牌优先型AI - 优先出小牌，保留大牌
    SMALL_FIRST = AIPersonalityConfig(
        name="小牌优先型",
        breaking_cost_factor=0.08,
        risk_factor=1.2,
        play_reward_factor=0.015,
        pass_penalty=0.15,
        small_card_priority=0.03,  # 小牌优先奖励
    )

    # 炸弹收藏家 - 特别重视保留炸弹
    BOMB_COLLECTOR = AIPersonalityConfig(
        name="炸弹收藏家",
        breaking_cost_factor=0.15,
        risk_factor=0.8,
        play_reward_factor=0.01,
        pass_penalty=0.1,
        bomb_value=3.0,  # 极高炸弹价值
    )

    # 辅助型AI - 专注于团队配合
    SUPPORTIVE = AIPersonalityConfig(
        name="辅助型",
        breaking_cost_factor=0.1,
        risk_factor=0.9,
        play_reward_factor=0.01,
        pass_penalty=0.1,
        team_cooperation_factor=0.5,  # 高团队合作系数
    )

    # 进攻型辅助 - 辅助队友的同时保持进攻性
    OFFENSIVE_SUPPORT = AIPersonalityConfig(
        name="进攻型辅助",
        breaking_cost_factor=0.07,
        risk_factor=1.3,
        play_reward_factor=0.02,
        pass_penalty=0.15,
        team_cooperation_factor=0.3,  # 中等团队合作系数
    )

    # 防守型辅助 - 更注重保护队友
    DEFENSIVE_SUPPORT = AIPersonalityConfig(
        name="防守型辅助",
        breaking_cost_factor=0.15,
        risk_factor=0.7,
        play_reward_factor=0.008,
        pass_penalty=0.08,
        team_cooperation_factor=0.7,  # 极高团队合作系数
    )
