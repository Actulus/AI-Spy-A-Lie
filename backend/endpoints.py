# endpoints.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from typing import List
from uuid import UUID
from database import get_db
from models import Highscore
import datetime

router = APIRouter()

class HighscoreCreate(BaseModel):
    user_name: str
    user_score: int
    room_socket_id: str
    ai_bot_type: str
    kinde_uuid: str
    profile_picture: str

class HighscoreResponse(BaseModel):
    id: UUID
    highscore_datetime: str
    user_name: str
    user_score: int
    room_socket_id: str
    ai_bot_type: str
    kinde_uuid: str
    profile_picture: str

    @validator('highscore_datetime', pre=True, always=True)
    def format_datetime(cls, value):
        if isinstance(value, datetime.datetime):
            return value.isoformat()
        return value

    class Config:
        from_attributes = True

@router.get('/highscores', response_model=List[HighscoreResponse])
def get_all_highscores(db: Session = Depends(get_db)):
    highscores = db.query(Highscore).order_by(Highscore.user_score.desc()).order_by(Highscore.highscore_datetime.desc()).all()
    return highscores

@router.get('/highscores/{kinde_uuid}', response_model=List[HighscoreResponse])
def get_highscore_for_user(kinde_uuid: str, db: Session = Depends(get_db)):
    highscores = db.query(Highscore).filter(Highscore.kinde_uuid == kinde_uuid).order_by(Highscore.user_score.desc()).order_by(Highscore.highscore_datetime.desc()).all()
    if not highscores:
        raise HTTPException(status_code=404, detail="No highscores found for this user")
    return highscores

@router.get('/highscores/{kinde_uuid}/best', response_model=HighscoreResponse)
def get_best_highscore_for_user(kinde_uuid: str, db: Session = Depends(get_db)):
    highscore = db.query(Highscore).filter(Highscore.kinde_uuid == kinde_uuid).order_by(Highscore.user_score.desc()).first()
    if not highscore:
        raise HTTPException(status_code=404, detail="No highscores found for this user")
    return highscore

@router.post('/highscores', response_model=HighscoreResponse)
def post_highscore(highscore: HighscoreCreate, db: Session = Depends(get_db)):
    db_highscore = Highscore(
        user_name=highscore.user_name,
        user_score=highscore.user_score,
        room_socket_id=highscore.room_socket_id,
        ai_bot_type=highscore.ai_bot_type,
        kinde_uuid=highscore.kinde_uuid,
        profile_picture=highscore.profile_picture,
    )
    db.add(db_highscore)
    db.commit()
    db.refresh(db_highscore)
    return db_highscore