import esper
import logging
import datetime
import sqlalchemy as sa
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 基础模型
Base = declarative_base()


class DatabaseSystem(esper.Processor):
    """
    数据库系统处理器，负责将游戏中的出牌记录保存到SQLite数据库。

    每局游戏会创建一个独立的表，表名格式为：'时间戳_模式_局数'
    """

    def __init__(self, db_file="logs/game_records.db"):
        """
        初始化数据库系统。

        参数:
            db_file (str): SQLite数据库文件路径
        """
        self.engine = create_engine(f"sqlite:///{db_file}")
        self.metadata = MetaData()
        self.Session = sessionmaker(bind=self.engine)
        self.session = None
        self.current_table = None
        self.current_table_name = None
        self.pending_records = []  # 存储待提交的记录

    def start_new_game(self, mode, game_number):
        """
        开始新游戏，创建新表。

        参数:
            mode (str): 游戏模式，'训练'或'评估'
            game_number (int): 当前局数
        """
        # 生成表名
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.current_table_name = f"{timestamp}_{mode}_{game_number}"

        # 动态创建表
        self.current_table = sa.Table(
            self.current_table_name,
            self.metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("player_id", Integer),
            Column("player_name", String),
            Column("action", String),  # 'PLAY' 或 'PASS'
            Column("cards_played", String),  # 以逗号分隔的卡牌
            Column("remaining_cards", Integer),  # 剩余手牌数量（通过current_hand计算）
            Column("current_hand", Text),  # 当前手牌，以逗号分隔
            Column("last_player_id", Integer),  # 新增：上一个打出牌的玩家ID
            Column("last_played_cards", String),  # 新增：上一个玩家打出的牌
            Column("timestamp", DateTime, default=datetime.datetime.utcnow),
        )

        # 创建表结构
        self.metadata.create_all(self.engine)
        self.session = self.Session()
        logging.debug(f"创建新的游戏记录表: {self.current_table_name}")

    def record_play(
        self,
        player_id,
        player_name,
        cards,
        current_hand,
        last_player_id=None,
        last_played_cards=None,
    ):
        """
        记录玩家出牌动作。

        参数:
            player_id (int): 玩家ID
            player_name (str): 玩家名称
            cards (list): 打出的卡牌列表
            current_hand (list): 出牌后的当前手牌列表
            last_player_id (int, optional): 上一个出牌的玩家ID
            last_played_cards (list, optional): 上一个玩家打出的卡牌列表
        """
        if self.current_table is None:
            logging.warning("尝试记录出牌但没有活动的游戏表")
            return

        cards_str = (
            ", ".join([card.get_rank_display() for card in cards]) if cards else ""
        )
        current_hand_str = (
            ", ".join([card.get_rank_display() for card in current_hand])
            if current_hand
            else ""
        )

        # 处理上一个玩家打出的牌
        last_played_cards_str = ""
        if last_played_cards:
            last_played_cards_str = ", ".join(
                [card.get_rank_display() for card in last_played_cards]
            )

        remaining_cards = len(current_hand)  # 从当前手牌计算剩余数量

        # 添加到待提交列表
        self.pending_records.append(
            {
                "player_id": player_id,
                "player_name": player_name,
                "action": "PLAY",
                "cards_played": cards_str,
                "remaining_cards": remaining_cards,
                "current_hand": current_hand_str,
                "last_player_id": last_player_id,
                "last_played_cards": last_played_cards_str,
                "timestamp": datetime.datetime.now(),
            }
        )

    def record_pass(
        self,
        player_id,
        player_name,
        current_hand,
        last_player_id=None,
        last_played_cards=None,
    ):
        """
        记录玩家PASS动作。

        参数:
            player_id (int): 玩家ID
            player_name (str): 玩家名称
            current_hand (list): 玩家当前手牌列表
            last_player_id (int, optional): 上一个出牌的玩家ID
            last_played_cards (list, optional): 上一个玩家打出的卡牌列表
        """
        if self.current_table is None:
            logging.warning("尝试记录PASS但没有活动的游戏表")
            return

        current_hand_str = (
            ", ".join([card.get_rank_display() for card in current_hand])
            if current_hand
            else ""
        )

        # 处理上一个玩家打出的牌
        last_played_cards_str = ""
        if last_played_cards:
            last_played_cards_str = ", ".join(
                [card.get_rank_display() for card in last_played_cards]
            )

        remaining_cards = len(current_hand)  # 从当前手牌计算剩余数量

        # 添加到待提交列表
        self.pending_records.append(
            {
                "player_id": player_id,
                "player_name": player_name,
                "action": "PASS",
                "cards_played": "",
                "remaining_cards": remaining_cards,
                "current_hand": current_hand_str,
                "last_player_id": last_player_id,
                "last_played_cards": last_played_cards_str,
                "timestamp": datetime.datetime.now(),
            }
        )

    def process(self):
        """
        处理器的主要执行方法，由ECS系统自动调用。

        将所有待提交的记录保存到数据库。
        """
        if not self.pending_records or self.session is None:
            return

        try:
            # 批量插入所有待处理记录
            self.session.execute(self.current_table.insert(), self.pending_records)
            self.session.commit()
            self.pending_records.clear()
        except Exception as e:
            logging.error(f"保存游戏记录到数据库时出错: {e}")
            self.session.rollback()

    def end_game(self):
        """结束当前游戏，关闭会话"""
        if self.session:
            # 确保所有待处理记录都已保存
            self.process()
            self.session.close()
            self.session = None
            self.current_table = None
            self.current_table_name = None
            logging.debug("游戏记录会话已关闭")
