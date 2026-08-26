from datetime import datetime
from datetime import timezone
from typing import List, Optional

from pydantic import BaseModel, Field

class Company(BaseModel):
    employer_name: str
    employer_logo: Optional[str] = None
    employer_website: Optional[str] = None

class Location(BaseModel):
    city: str
    province: Optional[str] = None
    country: str
    postal_code: Optional[str] = None
    remote: bool

class Salary(BaseModel):
    job_salary_string: Optional[str] = None
    job_salary_min: Optional[int] = None
    job_salary_max: Optional[int] = None
    job_salary_currency: Optional[str] = None

class EmbeddingInfo(BaseModel):
    status: str = "pending"
    pinecone_id: Optional[str] = None
    model: Optional[str] = None

class Job(BaseModel):
    id: str # this comes from the id of the job retrieved from job APIs
    source: str # JSearch API (canada) or Adzuna API (vietnam)
    title: str
    company: Company
    location: Location
    salary: Salary
    employment_type: Optional[str] = None
    job_description: Optional[str] = None
    skills: Optional[List[str]] = Field(default_factory=list)
    requirements: Optional[List[str]] = Field(default_factory=list)
    posted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    url: Optional[str] = None
    full_combined_text: Optional[str] = None
    embedding_info: Optional[EmbeddingInfo] = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True

