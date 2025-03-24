from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()


class PlayRecord(Base):
    __tablename__ = "play_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer)
    player_name = Column(String)
    cards_played = Column(String)  # Store as comma-separated values
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
