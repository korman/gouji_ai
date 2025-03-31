from enum import Enum


class PlayStrategy(Enum):
    # 基础策略（原有）
    PLAY_MINIMAL = "出最小值的一组牌"
    SPLIT_PLAY = "拆牌压制"
    BOMB_PLAY = "炸弹压制"
    SINGLE_PLAY = "出单牌"
    LONG_CHAIN_PLAY = "出5个以上的小值牌"
    BIG_JOKER_PLAY = "大王压制"
    SMALL_JOKER_PLAY = "小王压制"
    PASS = "过牌"

    # 新增团队配合策略 ★
    FEDERAL_SUPPORT = "联邦救援"  # 帮助联邦队友解围出牌
    SIGNAL_PASS = "信号过牌"  # 通过特定牌型向联邦传递信号
    TAKE_BURDEN = "扛牌担当"  # 主动承担压制对手主攻手的责任

    # 新增特殊规则策略 ★
    BURN_PLAY = "烧牌突击"  # 满足烧牌条件时强制拦截
    ACE_HUNTING = "追猎无头"  # 当对手成为无头时针对性打击
    SHIELD_MODE = "护盾模式"  # 保留关键牌防止被烧牌

    # 新增风险控制策略 ★
    BAIT_PLAY = "诱敌陷阱"  # 出中等强度牌引诱对手消耗大牌
    POWER_RESERVE = "保留实力"  # 刻意保留大牌到残局阶段
    DECOY_PLAY = "佯攻牵制"  # 制造假进攻方向分散对手火力

    # 新增态势感知策略 ★
    KING_CONTROL = "控场威慑"  # 通过保留大小王影响对手决策
    PRESSURE_MAINTAIN = "持续施压"  # 维持出牌权不让对手喘息
    ENDGAME_TRAP = "残局收割"  # 识别终局阶段启动收割模式
