import uuid
from datetime import datetime, timedelta
from core.llm import call_llm_json
from core.models import (
    Candidate,
    MatchResult,
    Assessment,
    AssessmentQuestion,
    AssessmentScore,
    InterviewSlot,
    ApplicationStatus,
)
from agents.recruiting.state import RecruitingState
from agents.recruiting.prompts import (
    EXTRACT_CANDIDATE_SYSTEM, EXTRACT_CANDIDATE_USER,
    MATCH_RESUME_SYSTEM, MATCH_RESUME_USER,
    GENERATE_ASSESSMENT_SYSTEM, GENERATE_ASSESSMENT_USER,
    SCORE_ASSESSMENT_SYSTEM, SCORE_ASSESSMENT_USER,
)
from config.settings import get_settings


def _log(state: RecruitingState, message: str) -> list[str]:
    existing = state.get("log") or []
    timestamp = datetime.utcnow().strftime("%H:%M:%S")
    return existing + [f"[{timestamp}] {message}"]


def extract_candidate_node(state: RecruitingState) -> dict:
    log = _log(state, "Extracting candidate profile from resume...")
    try:
        data = call_llm_json(
            EXTRACT_CANDIDATE_SYSTEM,
            EXTRACT_CANDIDATE_USER.format(resume_text=state["resume_text"])
        )
        candidate = Candidate(
            candidate_id=f"CAND-{uuid.uuid4().hex[:8].upper()}",
            name=state.get("candidate_name") or data.get("name", "Unknown"),
            email=state.get("candidate_email") or data.get("email", ""),
            raw_resume_text=state["resume_text"],
            extracted_skills=data.get("skills", []),
            years_of_experience=data.get("years_of_experience"),
            current_title=data.get("current_title"),
            education=data.get("education"),
        )
        log = _log({"log": log}, f"Extracted: {candidate.name}, {candidate.current_title}, {candidate.years_of_experience} yrs")
        return {"candidate": candidate.model_dump(), "log": log, "error": None}
    except Exception as e:
        return {"log": _log({"log": log}, f"ERROR in extraction: {e}"), "error": str(e)}


def match_resume_node(state: RecruitingState) -> dict:
    log = _log(state, "Scoring resume against job description...")
    try:
        req = state["requisition"]
        cand = state["candidate"]
        data = call_llm_json(
            MATCH_RESUME_SYSTEM,
            MATCH_RESUME_USER.format(
                title=req["title"],
                department=req["department"],
                required_skills=", ".join(req["required_skills"]),
                preferred_skills=", ".join(req["preferred_skills"]),
                min_experience_years=req["min_experience_years"],
                responsibilities="\n- ".join(req["responsibilities"]),
                qualifications="\n- ".join(req["qualifications"]),
                name=cand["name"],
                current_title=cand.get("current_title", "Not specified"),
                years_of_experience=cand.get("years_of_experience", "Not specified"),
                skills=", ".join(cand.get("extracted_skills", [])),
                education=cand.get("education", "Not specified"),
                resume_text=cand["raw_resume_text"],
            )
        )
        match = MatchResult(**data)
        settings = get_settings()
        proceed = match.score >= settings.match_score_threshold
        log = _log({"log": log}, f"Match score: {match.score:.1f}% — {'proceeding to assessment' if proceed else 'flagged for human review'}")
        return {
            "match_result": match.model_dump(),
            "proceed_to_assessment": proceed,
            "needs_human_review": not proceed,
            "status": ApplicationStatus.ASSESSMENT_SENT.value if proceed else ApplicationStatus.HUMAN_REVIEW.value,
            "log": log,
        }
    except Exception as e:
        return {"log": _log({"log": log}, f"ERROR in matching: {e}"), "error": str(e)}


def route_after_match(state: RecruitingState) -> str:
    if state.get("error"):
        return "error"
    if state.get("proceed_to_assessment"):
        return "generate_assessment"
    return "human_review_queue"


def human_review_queue_node(state: RecruitingState) -> dict:
    log = _log(state, f"Placed in human review queue. Awaiting HM decision.")
    return {"status": ApplicationStatus.HUMAN_REVIEW.value, "log": log}


def generate_assessment_node(state: RecruitingState) -> dict:
    log = _log(state, "Generating role-specific assessment questions...")
    try:
        req = state["requisition"]
        match = state["match_result"]
        dept = req["department"].lower()
        title = req["title"].lower()
        if "engineer" in title or "software" in title or "tech" in dept:
            role_category = "technical — mix of technical (2), behavioural (2), situational (1)"
            num_questions = 5
        elif "finance" in dept or "analyst" in title:
            role_category = "analytical — mix of numerical (2), situational (2), behavioural (1)"
            num_questions = 5
        else:
            role_category = "professional — mix of behavioural (3), situational (2)"
            num_questions = 5
        data = call_llm_json(
            GENERATE_ASSESSMENT_SYSTEM,
            GENERATE_ASSESSMENT_USER.format(
                num_questions=num_questions,
                role_category=role_category,
                title=req["title"],
                department=req["department"],
                required_skills=", ".join(req["required_skills"]),
                missing_skills=", ".join(match.get("missing_skills", [])),
                strengths=", ".join(match.get("strengths", [])),
            )
        )
        questions = [AssessmentQuestion(**q) for q in data["questions"]]
        assessment = Assessment(
            assessment_id=f"ASMT-{uuid.uuid4().hex[:8].upper()}",
            requisition_id=req["requisition_id"],
            candidate_id=state["candidate"]["candidate_id"],
            questions=questions,
        )
        log = _log({"log": log}, f"Assessment generated: {len(questions)} questions")
        return {
            "assessment": assessment.model_dump(),
            "status": ApplicationStatus.ASSESSMENT_SENT.value,
            "log": log,
        }
    except Exception as e:
        return {"log": _log({"log": log}, f"ERROR generating assessment: {e}"), "error": str(e)}


def score_assessment_node(state: RecruitingState) -> dict:
    log = _log(state, "Scoring assessment responses...")
    try:
        assessment = state["assessment"]
        answers = state.get("assessment_answers", {})
        req = state["requisition"]
        if not answers:
            return {"log": _log({"log": log}, "No answers submitted."), "proceed_to_interview": False}
        questions = {q["question_id"]: q for q in assessment["questions"]}
        qa_pairs = "\n\n".join([
            f"{q_id} ({questions[q_id]['question_type']}): {questions[q_id]['question_text']}\nAnswer: {answer}"
            for q_id, answer in answers.items() if q_id in questions
        ])
        expected_themes_map = {
            q["question_id"]: q["expected_themes"]
            for q in assessment["questions"]
        }
        data = call_llm_json(
            SCORE_ASSESSMENT_SYSTEM,
            SCORE_ASSESSMENT_USER.format(
                title=req["title"],
                qa_pairs=qa_pairs,
                expected_themes_map=expected_themes_map,
            )
        )
        score_result = AssessmentScore(**data)
        settings = get_settings()
        proceed = score_result.overall_score >= settings.assessment_score_threshold
        log = _log({"log": log}, f"Assessment score: {score_result.overall_score:.1f}% — {'proceeding to interview' if proceed else 'flagged for human review'}")
        return {
            "assessment_score": score_result.model_dump(),
            "proceed_to_interview": proceed,
            "needs_human_review": not proceed,
            "status": ApplicationStatus.INTERVIEW_SCHEDULED.value if proceed else ApplicationStatus.HUMAN_REVIEW.value,
            "log": log,
        }
    except Exception as e:
        return {"log": _log({"log": log}, f"ERROR scoring assessment: {e}"), "error": str(e)}


def route_after_assessment(state: RecruitingState) -> str:
    if state.get("error"):
        return "error"
    if state.get("proceed_to_interview"):
        return "schedule_interview"
    return "human_review_queue"


def schedule_interview_node(state: RecruitingState) -> dict:
    log = _log(state, "Generating interview slot options...")
    settings = get_settings()
    slots = []
    base = datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0)
    slot_times = [9, 10, 11, 14, 15, 16]
    interviewers = [
        ("Alex Morgan", "alex.morgan@company.com"),
        ("Sam Patel", "sam.patel@company.com"),
        ("Jordan Lee", "jordan.lee@company.com"),
    ]
    day_offset = 1
    while len(slots) < settings.interview_slots_count:
        candidate_day = base + timedelta(days=day_offset)
        if candidate_day.weekday() < 5:
            for hour in slot_times:
                if len(slots) >= settings.interview_slots_count:
                    break
                interviewer = interviewers[len(slots) % len(interviewers)]
                slot_dt = candidate_day.replace(hour=hour)
                slots.append(InterviewSlot(
                    slot_id=f"SLOT-{uuid.uuid4().hex[:6].upper()}",
                    datetime_iso=slot_dt.isoformat(),
                    interviewer_name=interviewer[0],
                    interviewer_email=interviewer[1],
                    duration_minutes=60,
                ))
        day_offset += 1
    log = _log({"log": log}, f"{len(slots)} interview slots generated across 2 weeks")
    return {
        "offered_slots": [s.model_dump() for s in slots],
        "status": ApplicationStatus.INTERVIEW_SCHEDULED.value,
        "log": log,
    }


def error_node(state: RecruitingState) -> dict:
    log = _log(state, f"Pipeline halted: {state.get('error', 'Unknown error')}")
    return {"log": log}