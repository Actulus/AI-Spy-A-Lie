from sqlalchemy import Column, String, DateTime, Boolean, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime, timezone

Base = declarative_base()

class Match(Base):
    __tablename__ = 'matches'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_date = Column(DateTime, default=datetime.now(timezone.utc))
    room_socket_id = Column(String, nullable=False)

class AIMatchHistory(Base):
    __tablename__ = 'ai_match_histories'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ai_type = Column(String, nullable=False)
    match_id = Column(UUID(as_uuid=True), nullable=False)
    score = Column(BigInteger, nullable=False)

class UserMatchHistory(Base):
    __tablename__ = 'user_match_histories'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_kinde_uuid = Column(String, nullable=False)
    match_id = Column(UUID(as_uuid=True), nullable=False)
    score = Column(BigInteger, nullable=False)

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kinde_uuid = Column(String, nullable=False, unique=True)
    profile_picture = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    user_name = Column(String, nullable=False)
    user_total_score = Column(BigInteger, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc))
    is_deleted = Column(Boolean, default=False)