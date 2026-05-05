from app.auth.dependencies import get_current_user_id
from app.core.config import settings
from app.services.user_service import get_db, get_user_by_id
from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session


def is_owner(user_id: int, current_user_id: int = Depends(get_current_user_id)):
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action."
        )
    return True


def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")


def is_premium_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user or user.plan != "PREMIUM":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action is only available to PREMIUM users."
        )
