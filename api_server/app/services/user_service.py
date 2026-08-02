import logging
from datetime import datetime

from app.auth.dependencies import get_current_user_id
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserPlanUpdate, UserResponse
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


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
        logger.warning(f"User with ID {user_id} not found")
        return None
    return user


def update_user_plan(user_id: int, data: UserPlanUpdate, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    expiry = data.plan_expiry

    if data.new_plan == "PREMIUM" and expiry is None:
        raise HTTPException(400, "PREMIUM requires expiry")

    if expiry == "" or expiry is None:
        expiry = None
    elif isinstance(expiry, str):
        expiry = datetime.fromisoformat(expiry)

    logger.info(
        f"Updating user {user_id} plan to {data.new_plan} with expiry {expiry}")
    user.plan = data.new_plan
    user.plan_expiry = expiry
    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        logger.error(f"Error updating user plan: {e}")
        db.rollback()
        raise HTTPException(500, "Failed to update user plan")
    return user
