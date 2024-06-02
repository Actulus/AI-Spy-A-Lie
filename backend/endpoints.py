# endpoints.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from typing import List
from uuid import UUID
from database import get_db
from models import Highscore
from sqlalchemy import func
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

    @validator("highscore_datetime", pre=True, always=True)
    def format_datetime(cls, value):
        if isinstance(value, datetime.datetime):
            return value.isoformat()
        return value

    class Config:
        from_attributes = True


class TotalHighscoreResponse(BaseModel):
    kinde_uuid: str
    total_score: int

    class Config:
        from_attributes = True


class UserTotalScoreResponse(BaseModel):
    kinde_uuid: str
    user_name: str
    user_score: int
    profile_picture: str

    class Config:
        from_attributes = True


@router.get("/highscores", response_model=List[HighscoreResponse])
def get_all_highscores(db: Session = Depends(get_db)):
    highscores = (
        db.query(Highscore)
        .order_by(Highscore.user_score.desc())
        .order_by(Highscore.highscore_datetime.desc())
        .all()
    )
    return highscores

@router.get("/highscores/total", response_model=List[UserTotalScoreResponse])
def get_all_users_total_highscores(db: Session = Depends(get_db)):
    all_users_uuid = db.query(Highscore.kinde_uuid).distinct().all()

    if not all_users_uuid:
        raise HTTPException(status_code=404, detail="No highscores found for any user")
    
    all_users_total_scores = []
    for user_uuid_tuple in all_users_uuid:
        user_uuid = user_uuid_tuple[0]
        total_score = (
            db.query(func.sum(Highscore.user_score))
            .filter(Highscore.kinde_uuid == user_uuid)
            .scalar()
        )
        user_info = db.query(Highscore).filter(Highscore.kinde_uuid == user_uuid).first()
        user_name = user_info.user_name
        profile_picture = user_info.profile_picture
        all_users_total_scores.append({
            "kinde_uuid": user_uuid,
            "user_name": user_name,
            "user_score": total_score,
            "profile_picture": profile_picture
        })

    # sort all_users_total_scores by total_score
    all_users_total_scores = sorted(all_users_total_scores, key=lambda x: x["user_score"], reverse=True)
    # return the top 10 users
    return all_users_total_scores[:10]


@router.get("/highscores/{kinde_uuid}", response_model=List[HighscoreResponse])
def get_highscore_for_user(kinde_uuid: str, db: Session = Depends(get_db)):
    highscores = (
        db.query(Highscore)
        .filter(Highscore.kinde_uuid == kinde_uuid)
        .order_by(Highscore.user_score.desc())
        .order_by(Highscore.highscore_datetime.desc())
        .all()
    )
    if not highscores:
        raise HTTPException(status_code=404, detail="No highscores found for this user")
    return highscores


@router.get("/highscores/{kinde_uuid}/best", response_model=HighscoreResponse)
def get_best_highscore_for_user(kinde_uuid: str, db: Session = Depends(get_db)):
    highscore = (
        db.query(Highscore)
        .filter(Highscore.kinde_uuid == kinde_uuid)
        .order_by(Highscore.user_score.desc())
        .first()
    )
    if not highscore:
        raise HTTPException(status_code=404, detail="No highscores found for this user")
    return highscore


@router.get("/highscores/{kinde_uuid}/total", response_model=TotalHighscoreResponse)
def get_total_highscore_for_user(kinde_uuid: str, db: Session = Depends(get_db)):
    total_score = (
        db.query(func.sum(Highscore.user_score))
        .filter(Highscore.kinde_uuid == kinde_uuid)
        .scalar()
    )

    if not total_score:
        raise HTTPException(status_code=404, detail="No highscores found for this user")

    return {"kinde_uuid": kinde_uuid, "total_score": total_score}





@router.post("/highscores", response_model=HighscoreResponse)
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
