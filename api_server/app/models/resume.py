from datetime import datetime, timezone
from typing import Optional, List

from pydantic import BaseModel, Field

class ResumeAnalysis(BaseModel):
    user_id: int
    resume_id: int

    # Analysis of the resume

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Resume(BaseModel):
    user_id: int
    resume_id: int
    filename: str
    storage_path: Optional[str] = None # will be implemented in the future
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResumeForJobRecommendation(BaseModel):
    user_id: int
    # Latest analysis of the resume
    resume_id: int
    full_combined_text: str