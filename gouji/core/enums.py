class PlayStrategy(Enum):
    """出牌策略枚举"""
    PLAY_MINIMAL = "出最小值的一组牌"  # 出最小点数的牌组
    SPLIT_PLAY = "拆牌压制"           # 需要拆散更大组合的牌来压制
    BOMB_PLAY = "炸弹压制"           # 使用炸弹(四张相同点数)压制
    SINGLE_PLAY = "出单牌"           # 出单张牌
    LONG_CHAIN_PLAY = "出5个以上的小值牌"  # 出5张以上相同点数的牌
    BIG_JOKER_PLAY = "大王压制"      # 使用大王
    SMALL_JOKER_PLAY = "小王压制"    # 使用小王
    PASS = "过牌"                   # 选择不出牌
