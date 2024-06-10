from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from uuid import UUID
from database import get_db
from models import User, UserMatchHistory, AIMatchHistory, Match
import datetime

router = APIRouter()

class UserCreate(BaseModel):
    kinde_uuid: str
    profile_picture: str
    user_name: str


class UserResponse(BaseModel):
    id: UUID
    kinde_uuid: str
    profile_picture: str
    is_admin: bool
    user_name: str
    user_total_score: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    is_deleted: bool

    # class Config:
    #     orm_mode = True
    

class OpponentResponse(BaseModel):
    user_name: str
    score: int

class AIOpponentResponse(BaseModel):
    ai_type: str
    score: int

class UserMatchHistoryResponse(BaseModel):
    match_id: UUID
    match_date: datetime
    user_score: int
    opponents: List[OpponentResponse]
    ai_opponents: List[AIOpponentResponse]

    class Config:
        arbitrary_types_allowed = True

class MatchResponse(BaseModel):
    id: UUID
    match_date: datetime.datetime
    room_socket_id: str

    class Config:
        orm_mode = True


class MatchCreate(BaseModel):
    socket_id: str
    users: List[dict]
    ai_opponents: List[dict]


def update_user_total_score(kinde_uuid: str, score: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.kinde_uuid == kinde_uuid).first()
    db_user.user_total_score += score
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/match", response_model=MatchResponse)
def create_match(match_data: MatchCreate, db: Session = Depends(get_db)):
    # log the match data
    print(match_data)
    
    # Create a new match with the current date and socket ID
    new_match = Match(
        match_date=datetime.datetime.now(),
        room_socket_id=match_data.socket_id
    )
    db.add(new_match)
    db.commit()
    db.refresh(new_match)


    # Create user match histories for each user and their score
    for user_data in match_data.users:
        user_match_history = UserMatchHistory(
            match_id=new_match.id,
            user_kinde_uuid=user_data["kinde_uuid"],
            score=user_data["score"]
        )
        db.add(user_match_history)
        db.commit()
        db.refresh(user_match_history)

        # Update the total user score for each user based on their score in the match
        update_user_total_score(user_data["kinde_uuid"], user_data["score"], db)

    # Create AI match histories for each AI opponent and their score
    for ai_data in match_data.ai_opponents:
        ai_match_history = AIMatchHistory(
            match_id=new_match.id,
            ai_type=ai_data["ai_type"],
            score=ai_data["score"]
        )
        db.add(ai_match_history)
        db.commit()
        db.refresh(ai_match_history)

    return new_match


@router.post("/user", response_model=UserResponse)
def create_or_get_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.kinde_uuid == user.kinde_uuid).first()
    if db_user:
        return db_user
    else:
        new_user = User(
            kinde_uuid=user.kinde_uuid,
            profile_picture=user.profile_picture,
            user_name=user.user_name
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

@router.get("/users/leaderboard", response_model=List[UserResponse])
def get_leaderboard(db: Session = Depends(get_db)):
    leaderboard = db.query(User).order_by(User.user_total_score.desc()).limit(10).all()
    return leaderboard

@router.get("/users/{kinde_uuid}", response_model=UserResponse)
def get_user(kinde_uuid: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.kinde_uuid == kinde_uuid).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.get("/users/{kinde_uuid}/match-histories", response_model=List[UserMatchHistoryResponse])
def get_user_match_histories(kinde_uuid: str, db: Session = Depends(get_db)):
    user_match_histories = db.query(UserMatchHistory).filter(UserMatchHistory.user_kinde_uuid == kinde_uuid).all()
    
    match_history_responses = []
    for user_match_history in user_match_histories:
        match = db.query(Match).filter(Match.id == user_match_history.match_id).first()
        
        opponents = []
        other_user_match_histories = db.query(UserMatchHistory).filter(
            UserMatchHistory.match_id == user_match_history.match_id,
            UserMatchHistory.user_kinde_uuid != kinde_uuid
        ).all()

        for other_user_match_history in other_user_match_histories:
            other_user = db.query(User).filter(User.kinde_uuid == other_user_match_history.user_kinde_uuid).first()
            opponents.append(OpponentResponse(user_name=other_user.user_name, score=other_user_match_history.score))
        
        ai_opponents = []
        ai_match_histories = db.query(AIMatchHistory).filter(AIMatchHistory.match_id == user_match_history.match_id).all()
        for ai_match_history in ai_match_histories:
            ai_opponents.append(AIOpponentResponse(ai_type=ai_match_history.ai_type, score=ai_match_history.score))
        
        match_history_response = UserMatchHistoryResponse(
            match_id=user_match_history.match_id,
            match_date=match.match_date,
            user_score=user_match_history.score,
            opponents=opponents,
            ai_opponents=ai_opponents
        )
        match_history_responses.append(match_history_response)
    
    return match_history_responses

@router.get("/users/{kinde_uuid}/total-score", response_model=dict)
def get_user_total_score(kinde_uuid: str, db: Session = Depends(get_db)):
    user_total_score = db.query(User).filter(User.kinde_uuid == kinde_uuid).first().user_total_score
    
    return {"user_total_score": user_total_score}


