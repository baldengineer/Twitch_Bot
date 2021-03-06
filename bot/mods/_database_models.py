from asyncio import sleep
from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import orm
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
from twitchbot import Mod
from twitchbot.config import mysql_cfg
from twitchbot.util import add_task
from twitchbot.util import task_running


Base = declarative_base()


class Users(Base):
    """Storing user data"""

    __tablename__ = "users"
    # __table_args__ = {"extend_existing": True}
    user_id = Column(Integer(), primary_key=True, nullable=False, index=True)
    channel = Column(Integer(), primary_key=True, nullable=False, index=True)
    user = Column(String(64), unique=True)
    time_in_channel = Column(Integer(), default=0)
    message_count = Column(Integer(), default=0)
    cheers = Column(Integer(), default=0)
    last_update = Column(DateTime(), onupdate=datetime.now)
    last_message = Column(DateTime())


class Subscriptions(Base):
    """Store subscription info"""

    __tablename__ = "subscriptions"
    # __table_args__ = {"extend_existing": True}
    user_id = Column(Integer(), ForeignKey("users.user_id"), primary_key=True, nullable=False, index=True)
    channel = Column(Integer(), ForeignKey("users.channel"), primary_key=True, nullable=False, index=True)
    subscription_level = Column(String(64))
    cumulative_months = Column(Integer(), default=0)
    streak_months = Column(Integer(), default=0)


class Announcements(Base):
    """Storing data for the announcements command"""

    # Keep in sync with /web/models.py for fastapi to use

    __tablename__ = "announcements"
    # __table_args__ = {"extend_existing": True}
    id = Column(Integer(), primary_key=True, nullable=False)
    text = Column(String(1024), nullable=False)
    created_date = Column(DateTime(), default=datetime.now)
    last_sent = Column(DateTime(), default=datetime.now)
    times_sent = Column(Integer(), default=0)
    enabled = Column(Boolean(), default=True)


class Settings(Base):
    """Used for storing random bot settings"""

    __tablename__ = "settings"
    # __table_args__ = {"extend_existing": True}
    id = Column(Integer(), primary_key=True)
    key = Column(String(128), nullable=False, unique=True)
    value = Column(String(1024), nullable=False)


# Put all Table classes above here
class Database(Mod):
    name = "database"

    def __init__(self) -> None:
        super().__init__()

        engine = create_engine(
            f"mysql+mysqlconnector://{mysql_cfg.username}:{mysql_cfg.password}@{mysql_cfg.address}:{mysql_cfg.port}/{mysql_cfg.database}"  # noqa E501
        )
        Session = orm.sessionmaker(bind=engine, autoflush=True)
        self.session = orm.scoped_session(Session)
        Base.metadata.create_all(engine)


# Define the session before the keep_alive_loop so it's available to it
session = Database().session


async def keep_alive_loop():
    while True:
        session.query(Settings).filter(Settings.key == "keepalive").one_or_none()
        print("Mysql keep-alive running...")

        await sleep(3600)  # Run the keep alive once an hour


# Start the keep-alive loop if it's not running
if not task_running("mysql-keepalive"):
    add_task("mysql-keepalive", keep_alive_loop())
