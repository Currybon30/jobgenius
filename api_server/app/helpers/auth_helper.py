from typing import Annotated
from app.auth.dependencies import get_current_user_id
from app.core.config import settings
from app.schemas.user import PlanEnum, UserResponse
from app.services.user_service import get_current_user, get_db, get_user_by_id
from fastapi import Depends, Header, HTTPException, Request, status


def is_owner(user_id: int, current_user: Annotated[UserResponse, Depends(get_current_user)]):
    if current_user.uid != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action."
        )
    return True


def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")


def is_premium_user(current_user: Annotated[UserResponse, Depends(get_current_user)]):
    if not current_user or current_user.plan != PlanEnum.PREMIUM:
        return False
    return True