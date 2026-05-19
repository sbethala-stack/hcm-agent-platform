from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime


class ApplicationStatus(str, Enum):
    RECEIVED = "received"
    SCREENING = "screening"
    HUMAN_REVIEW = "human_review"
    ASSESSMENT_SENT = "assessment_sent"
    ASSESSMENT_SCORED = "assessment_scored"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    REJECTED = "rejected"
    OFFER_PENDING = "offer_pending"


class Candidate(BaseModel):
    candidate_id: str
    name: str
    email: str
    raw_resume_text: str
    extracted_skills: list[str] = Field(default_factory=list)
    years_of_experience: Optional[float] = None
    current_title: Optional[str] = None
    education: Optional[str] = None


class JobRequisition(BaseModel):
    requisition_id: str
    title: str
    department: str
    required_skills: list[str]
    preferred_skills: list[str]
    min_experience_years: float
    description: str
    responsibilities: list[str]
    qualifications: list[str]


class MatchResult(BaseModel):
    score: float = Field(ge=0, le=100)
    matched_skills: list[str]
    missing_skills: list[str]
    experience_gap: Optional[str] = None
    strengths: list[str]
    weaknesses: list[str]
    summary: str


class AssessmentQuestion(BaseModel):
    question_id: str
    question_text: str
    question_type: str
    expected_themes: list[str]


class Assessment(BaseModel):
    assessment_id: str
    requisition_id: str
    candidate_id: str
    questions: list[AssessmentQuestion]
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class AssessmentScore(BaseModel):
    overall_score: float = Field(ge=0, le=100)
    question_scores: dict[str, float]
    feedback_per_question: dict[str, str]
    overall_feedback: str


class InterviewSlot(BaseModel):
    slot_id: str
    datetime_iso: str
    interviewer_name: str
    interviewer_email: str
    duration_minutes: int = 60


class ApplicationRecord(BaseModel):
    application_id: str
    candidate_id: str
    requisition_id: str
    status: ApplicationStatus = ApplicationStatus.RECEIVED
    match_result: Optional[MatchResult] = None
    assessment: Optional[Assessment] = None
    assessment_score: Optional[AssessmentScore] = None
    offered_slots: list[InterviewSlot] = Field(default_factory=list)
    selected_slot: Optional[InterviewSlot] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)