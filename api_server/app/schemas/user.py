from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class PlanEnum(str, Enum):
    FREE = "FREE"
    PREMIUM = "PREMIUM"


# 🔹 Response (what API returns)
class UserResponse(BaseModel):
    uid: int
    plan: str
    plan_expiry: Optional[datetime] = None

    class Config:
        orm_mode = True


# 🔹 Create (if needed)
class UserCreate(BaseModel):
    uid: int
    plan: PlanEnum = PlanEnum.FREE
    plan_expiry: Optional[datetime] = None


# 🔹 Update plan
class UserPlanUpdate(BaseModel):
    new_plan: PlanEnum
    plan_expiry: Optional[datetime] = None
