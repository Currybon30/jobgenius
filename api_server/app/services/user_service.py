from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.auth.dependencies import get_current_user_id
from app.models.user import User

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.uid == user_id).first()

def add_user_to_db(user_id: int, db: Session = Depends(get_db)):
    new_user = User()
    new_user.uid = user_id
    new_user.plan = "FREE"
    new_user.plan_expiry = None
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_current_user(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    return user

def update_user_plan(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id), new_plan: str = "FREE", plan_expiry: str = None):
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    user.plan = new_plan
    user.plan_expiry = plan_expiry
    db.commit()
    db.refresh(user)
    return user