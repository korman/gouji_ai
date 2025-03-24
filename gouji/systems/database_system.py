import esper
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .db import Base, PlayRecord


class DatabaseSystem(esper.Processor):
    def __init__(self, db_file):
        self.engine = create_engine(f"sqlite:///{db_file}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def record_play(self, player_id, player_name, cards):
        cards_str = ", ".join([card.get_rank_display() for card in cards])
        new_record = PlayRecord(
            player_id=player_id, player_name=player_name, cards_played=cards_str
        )
        self.session.add(new_record)
        self.session.commit()

    def process(self):
        pass  # No need to process per frame
