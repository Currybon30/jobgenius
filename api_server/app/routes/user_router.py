from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Header, status
from fastapi.params import Body
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserPlanUpdate, UserResponse
from app.db.session import get_db
from app.services.user_service import get_current_user, update_user_plan, get_user_by_id, add_user_to_db
from app.models.user import User
from app.helpers.auth_helper import is_owner, verify_api_key
router = APIRouter(tags=["users"])
from app.core.config import settings

@router.get("/api/users", response_model=UserResponse) # Query user info by user_id, only accessible by the user themselves
def get_user_info(user_id: int, current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    if not is_owner(current_user.uid, user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.get("/api/users/me", response_model=UserResponse)
def get_current_user_info(current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return current_user

@router.post("/internal/users/add", response_model=UserResponse)
def add_user(db: Annotated[Session, Depends(get_db)], x_api_key: Annotated[str, Header(...)], data: UserCreate):
    verify_api_key(x_api_key)
    existing_user = get_user_by_id(db, data.uid)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    new_user = add_user_to_db(data.uid, db)
    return new_user

@router.put("/internal/users/{user_id}/plan/update", response_model=UserResponse)
def update_user_subscription_plan(user_id: int, db: Annotated[Session, Depends(get_db)], x_api_key: Annotated[str, Header(...)], data: UserPlanUpdate):
    verify_api_key(x_api_key)
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    updated_user = update_user_plan(user_id=user_id, data=data, db=db)
    return updated_user