from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime, timezone

Base = declarative_base()

class Highscore(Base):
    __tablename__ = 'highscores'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    highscore_datetime = Column(DateTime, default=datetime.now(timezone.utc))
    user_name = Column(String, nullable=False)
    user_score = Column(Integer, nullable=False)
    room_socket_id = Column(String, nullable=False)
    ai_bot_type = Column(String, nullable=False)
    kinde_uuid = Column(String, nullable=False)
    profile_picture = Column(String, nullable=False)