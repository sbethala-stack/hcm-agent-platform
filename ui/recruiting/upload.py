import streamlit as st
from core.resume_parser import extract_text_from_pdf
from core.models import ApplicationStatus
from connectors.mock_erp.seed_data import REQUISITIONS
from agents.recruiting.graph import recruiting_graph
from agents.recruiting.nodes import score_assessment_node, schedule_interview_node
from ui.session import get_erp, get_agent_states, save_agent_state, get_agent_state


def render_upload_page():
    st.title("Resume Screening")
    st.caption("Upload a resume to run the full recruiting pipeline")

    erp = get_erp()

    with st.container(border=True):
        st.subheader("1. Select Role & Upload Resume")

        col1, col2 = st.columns(2)
        with col1:
            req_options = {f"{r.requisition_id} — {r.title}": r.requisition_id for r in REQUISITIONS}
            selected_label = st.selectbox("Job Requisition", options=list(req_options.keys()))
            requisition_id = req_options[selected_label]
            req = erp.get_requisition(requisition_id)

        with col2:
            uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
            candidate_name = st.text_input("Candidate Name", placeholder="Jane Smith")
            candidate_email = st.text_input("Candidate Email", placeholder="jane@example.com")

        if req:
            with st.expander("View Job Description"):
                st.markdown(f"**{req.title}** | {req.department}")
                st.write(req.description)
                st.markdown("**Required Skills:** " + ", ".join(req.required_skills))
                st.markdown("**Preferred Skills:** " + ", ".join(req.preferred_skills))
                st.markdown(f"**Min Experience:** {req.min_experience_years} years")

        run_disabled = not (uploaded_file and candidate_name and candidate_email)
        run_btn = st.button(
            "Run Agent Pipeline",
            type="primary",
            disabled=run_disabled,
        )

    if run_btn and uploaded_file:
        _run_pipeline(erp, uploaded_file, candidate_name, candidate_email, requisition_id, req)

    _render_active_application()
def _run_pipeline(erp, uploaded_file, candidate_name, candidate_email, requisition_id, req):
    file_bytes = uploaded_file.read()

    with st.status("Running agent pipeline...", expanded=True) as status:
        st.write("Extracting text from resume...")
        resume_text = extract_text_from_pdf(file_bytes)

        if not resume_text or len(resume_text.strip()) < 50:
            st.error("Could not extract text from PDF. Please try a text-based PDF.")
            return

        app_record = erp.create_application(
            requisition_id=requisition_id,
            candidate_name=candidate_name,
            candidate_email=candidate_email,
            resume_text=resume_text,
        )
        app_id = app_record.application_id
        st.write(f"Application created: `{app_id}`")
        st.write("Running LLM pipeline...")

        initial_state = {
            "resume_text": resume_text,
            "candidate_name": candidate_name,
            "candidate_email": candidate_email,
            "requisition_id": requisition_id,
            "requisition": req.model_dump(),
            "application_id": app_id,
            "candidate": None,
            "match_result": None,
            "assessment": None,
            "assessment_answers": None,
            "assessment_score": None,
            "offered_slots": None,
            "selected_slot": None,
            "status": None,
            "needs_human_review": False,
            "proceed_to_assessment": False,
            "proceed_to_interview": False,
            "log": [],
            "error": None,
        }

        final_state = {**initial_state}
        for event in recruiting_graph.stream(initial_state):
            for node_name, node_output in event.items():
                if node_name == "__end__":
                    continue
                log_entries = node_output.get("log", [])
                if log_entries:
                    st.write(f"✓ `{node_name}`: {log_entries[-1].split('] ', 1)[-1]}")
                final_state.update(node_output)

        final_state["application_id"] = app_id
        save_agent_state(app_id, final_state)
        st.session_state["active_application_id"] = app_id
        status.update(label="Pipeline complete", state="complete")

    st.rerun()
def _render_active_application():
    app_id = st.session_state.get("active_application_id")
    if not app_id:
        return

    state = get_agent_state(app_id)
    if not state:
        return

    st.divider()

    with st.expander("Agent Activity Log", expanded=False):
        for entry in state.get("log", []):
            st.text(entry)

    match = state.get("match_result")
    if match:
        _render_match_report(state, match)

    if state.get("needs_human_review") and not state.get("proceed_to_assessment"):
        _render_human_review_panel(app_id, state)
        return

    assessment = state.get("assessment")
    if assessment and not state.get("assessment_score"):
        _render_assessment_form(app_id, state, assessment)

    asmt_score = state.get("assessment_score")
    if asmt_score:
        _render_assessment_score(asmt_score)

    if asmt_score and state.get("needs_human_review") and not state.get("proceed_to_interview"):
        _render_human_review_panel(app_id, state, after_assessment=True)
        return

    if state.get("offered_slots"):
        _render_interview_slots(app_id, state)
def _render_match_report(state, match):
    score = match["score"]
    threshold = 65.0

    st.subheader("Match Report")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Match Score",
            f"{score:.1f}%",
            delta=f"{score - threshold:+.1f}% vs threshold",
            delta_color="normal" if score >= threshold else "inverse"
        )
    with col2:
        st.metric("Matched Skills", len(match["matched_skills"]))
    with col3:
        st.metric("Missing Skills", len(match["missing_skills"]))

    cand = state.get("candidate", {})
    st.markdown(f"**Candidate:** {cand.get('name', '—')} | {cand.get('current_title', '—')} | {cand.get('years_of_experience', '—')} yrs exp")

    with st.container(border=True):
        st.markdown("**Summary**")
        st.write(match["summary"])

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Strengths**")
            for s in match["strengths"]:
                st.markdown(f"- {s}")
            st.markdown("**Matched Skills**")
            st.write(", ".join(match["matched_skills"]) or "None")
        with col2:
            st.markdown("**Areas of Concern**")
            for w in match["weaknesses"]:
                st.markdown(f"- {w}")
            st.markdown("**Missing Skills**")
            st.write(", ".join(match["missing_skills"]) or "None")
            if match.get("experience_gap"):
                st.markdown(f"**Experience Note:** {match['experience_gap']}")

    if score >= threshold:
        st.success("Score ≥ 65% — Assessment automatically triggered")
    else:
        st.warning("Score < 65% — Placed in human review queue. No auto-rejection.")
def _render_human_review_panel(app_id, state, after_assessment=False):
    st.subheader("Human Review Required")
    context = "assessment score" if after_assessment else "match score"
    st.info(f"This candidate's {context} is below threshold. Please review and decide.")

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Approve — Proceed to Next Step", type="primary", key=f"approve_{app_id}_{after_assessment}"):
                updated = {**state}
                updated["needs_human_review"] = False
                updated["log"] = state.get("log", []) + ["[HM Decision] Manually approved"]

                if not after_assessment:
                    from agents.recruiting.nodes import generate_assessment_node
                    with st.spinner("Generating assessment..."):
                        result = generate_assessment_node(updated)
                        updated.update(result)
                else:
                    with st.spinner("Generating interview slots..."):
                        result = schedule_interview_node(updated)
                        updated.update(result)

                save_agent_state(app_id, updated)
                st.rerun()

        with col2:
            if st.button("❌ Reject Application", key=f"reject_{app_id}_{after_assessment}"):
                updated = {**state}
                updated["status"] = ApplicationStatus.REJECTED.value
                updated["log"] = state.get("log", []) + ["[HM Decision] Manually rejected"]
                save_agent_state(app_id, updated)
                st.rerun()

    if state.get("status") == ApplicationStatus.REJECTED.value:
        st.error("Application rejected.")
def _render_assessment_form(app_id, state, assessment):
    st.subheader("Assessment")
    st.info("Auto-generated based on role and candidate profile. In production this would be emailed to the candidate.")

    questions = assessment["questions"]
    answers = {}

    with st.form(key=f"assessment_form_{app_id}"):
        for q in questions:
            st.markdown(f"**{q['question_id']} ({q['question_type'].title()}):** {q['question_text']}")
            ans = st.text_area(
                label=f"Answer to {q['question_id']}",
                key=f"ans_{q['question_id']}",
                height=120,
                label_visibility="collapsed",
                placeholder="Type candidate response here..."
            )
            answers[q["question_id"]] = ans
            st.divider()

        submitted = st.form_submit_button("Submit & Score Assessment", type="primary")

    if submitted:
        if not all(v.strip() for v in answers.values()):
            st.warning("Please fill in all answers before submitting.")
            return

        with st.spinner("Scoring assessment responses..."):
            updated = {**state, "assessment_answers": answers}
            result = score_assessment_node(updated)
            updated.update(result)

            if updated.get("proceed_to_interview"):
                slot_result = schedule_interview_node(updated)
                updated.update(slot_result)

        save_agent_state(app_id, updated)
        st.rerun()
def _render_assessment_score(asmt_score):
    st.subheader("Assessment Results")
    score = asmt_score["overall_score"]
    threshold = 75.0

    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric(
            "Assessment Score",
            f"{score:.1f}%",
            delta=f"{score - threshold:+.1f}% vs threshold",
            delta_color="normal" if score >= threshold else "inverse"
        )
    with col2:
        st.write(asmt_score["overall_feedback"])

    with st.expander("Detailed Question Scores"):
        for q_id, q_score in asmt_score.get("question_scores", {}).items():
            col1, col2 = st.columns([1, 5])
            with col1:
                st.metric(q_id, f"{q_score:.0f}%")
            with col2:
                st.write(asmt_score.get("feedback_per_question", {}).get(q_id, ""))

    if score >= threshold:
        st.success("Score ≥ 75% — Interview scheduling triggered")
    else:
        st.warning("Score < 75% — Flagged for human review")


def _render_interview_slots(app_id, state):
    st.subheader("Interview Scheduling")
    st.success("Assessment passed. Select an interview slot.")
    st.info("In production: candidate and interviewers receive slot options by email.")

    slots = state.get("offered_slots", [])
    selected_slot = state.get("selected_slot")

    if selected_slot:
        dt = selected_slot["datetime_iso"][:16].replace("T", " at ")
        st.success(f"✅ Interview confirmed: {dt} with {selected_slot['interviewer_name']}")
        return

    cols = st.columns(3)
    for i, slot in enumerate(slots):
        with cols[i % 3]:
            dt_str = slot["datetime_iso"][:16].replace("T", " ")
            if st.button(
                f"{dt_str}\n{slot['interviewer_name']}",
                key=f"slot_{slot['slot_id']}",
                use_container_width=True,
            ):
                updated = {**state, "selected_slot": slot}
                updated["log"] = state.get("log", []) + [f"Interview slot selected: {dt_str}"]
                save_agent_state(app_id, updated)
                st.rerun()