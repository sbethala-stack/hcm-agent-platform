from typing import Optional
from typing_extensions import TypedDict


class RecruitingState(TypedDict):
    # Inputs — provided at the start
    resume_text: str
    candidate_name: str
    candidate_email: str
    requisition_id: str

    # Populated by nodes as pipeline progresses
    candidate: Optional[dict]
    requisition: Optional[dict]
    application_id: Optional[str]
    match_result: Optional[dict]
    assessment: Optional[dict]
    assessment_answers: Optional[dict]
    assessment_score: Optional[dict]
    offered_slots: Optional[list]
    selected_slot: Optional[dict]
    status: Optional[str]

    # Control flow flags — nodes set these to direct routing
    needs_human_review: bool
    proceed_to_assessment: bool
    proceed_to_interview: bool

    # Audit trail — every node appends a log entry
    log: list[str]

    # Error tracking
    error: Optional[str]