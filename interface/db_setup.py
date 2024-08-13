from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy_utils import database_exists, create_database

engine = create_engine("sqlite:///players.db")
if not database_exists(engine.url):
    create_database(engine.url)

print(database_exists(engine.url))

class Base(DeclarativeBase):
    pass

class Players():
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    player_name = Column(String(30))
    aoe2_insights_id = Column(Integer)
