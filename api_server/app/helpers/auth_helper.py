from datetime import datetime, timezone
from typing import Annotated

from app.core.config import settings
from app.db.session import get_db
from app.schemas.user import PlanEnum, UserPlanUpdate, UserResponse
from app.services.user_service import get_current_user, update_user_plan
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session


def is_owner(
    user_id: int, current_user: Annotated[UserResponse, Depends(get_current_user)]
):
    if current_user.uid != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action.",
        )
    return True


def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")


def is_premium_user(
    current_user: Annotated[UserResponse | None, Depends(get_current_user)],
):
    if not current_user:
        return False
    return current_user.plan == PlanEnum.PREMIUM
