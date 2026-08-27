from datetime import datetime, timezone
from typing import Optional, List

from bson import ObjectId
from pydantic import BaseModel, Field

class ResumeAnalysis(BaseModel):
    # Analysis of the resume
    # Intent agent
    target_role: str
    seniority_level: str
    industry: str
    priority_goals: List[str]
    focus_areas: List[str]
    top_keywords: List[str]
    optimization_strategy: dict
    # Analyzer agent
    sections: List[str]
    years_exp: int
    emails: List[str]
    phone_numbers: List[str]
    hard_skills: List[str]
    soft_skills: List[str]
    missing_hard_skills: Optional[List[str]]
    matching_hard_skills_score: Optional[float]
    missing_soft_skills: Optional[List[str]]
    matching_soft_skills_score: Optional[float]
    # ATS agent
    resume_score: float
    section_score: float
    experience_projects_score: float
    skills_quality_score: float
    summary_quality_score: float
    formatting_score: float
    ats_score: Optional[float]
    hard_skills_score: Optional[float]
    soft_skills_score: Optional[float]
    # Optimizer agent
    optimized_resume: str
    optimized_sections: dict
    keywords_integrated: List[str]
    changes_made: List[str]
    suggested_additions_if_true: List[str]
    optimization_notes: str
    # Finalizer agent
    summary: str
    skills_feedback: str
    experience_feedback: str
    structure_feedback: str
    simple_suggestions: List[str]

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Resume(BaseModel):
    id: ObjectId
    user_id: int
    resume_id: str
    version: int = 1
    filename: str
    storage_path: Optional[str] = None # will be implemented in the future
    analysis: ResumeAnalysis
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResumeForJobRecommendation(BaseModel):
    user_id: int
    # Latest analysis of the resume
    resume_id: str
    version: int = 1
    full_combined_text: str