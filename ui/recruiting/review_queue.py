import streamlit as st
from core.models import ApplicationStatus
from ui.session import get_agent_states, get_agent_state, save_agent_state
from agents.recruiting.nodes import schedule_interview_node


def render_review_queue():
    st.title("Human Review Queue")
    st.caption("Applications requiring hiring manager decision")

    states = get_agent_states()

    review_apps = [
        (app_id, s) for app_id, s in states.items()
        if s.get("needs_human_review")
        and s.get("status") != ApplicationStatus.REJECTED.value
    ]

    if not review_apps:
        st.info("No applications currently in the review queue.")
        return

    st.metric("Pending Review", len(review_apps))
    st.divider()

    for app_id, state in review_apps:
        cand = state.get("candidate", {})
        req = state.get("requisition", {})
        match = state.get("match_result", {})
        asmt_score = state.get("assessment_score")

        with st.expander(
            f"{'🔵' if not asmt_score else '🟡'} {cand.get('name', app_id)} — {req.get('title', '—')} | Match: {match.get('score', 0):.1f}%",
            expanded=True
        ):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Match Score", f"{match.get('score', 0):.1f}%")
            with col2:
                if asmt_score:
                    st.metric("Assessment Score", f"{asmt_score.get('overall_score', 0):.1f}%")
            with col3:
                st.metric("Application ID", app_id)

            st.write(f"**Candidate:** {cand.get('name')} | {cand.get('current_title', '—')} | {cand.get('years_of_experience', '—')} yrs")
            st.write(f"**Role:** {req.get('title')} | {req.get('department')}")

            if match.get("summary"):
                st.write(f"**Summary:** {match['summary']}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Approve", key=f"q_approve_{app_id}", type="primary"):
                    _approve(app_id, state, after_assessment=bool(asmt_score))
                    st.rerun()
            with col2:
                if st.button("❌ Reject", key=f"q_reject_{app_id}"):
                    updated = {**state}
                    updated["status"] = ApplicationStatus.REJECTED.value
                    updated["needs_human_review"] = False
                    updated["log"] = state.get("log", []) + ["[HM Decision] Rejected from queue"]
                    save_agent_state(app_id, updated)
                    st.rerun()


def _approve(app_id, state, after_assessment=False):
    updated = {**state}
    updated["needs_human_review"] = False

    if after_assessment:
        updated["proceed_to_interview"] = True
        result = schedule_interview_node(updated)
        updated.update(result)
    else:
        from agents.recruiting.nodes import generate_assessment_node
        updated["proceed_to_assessment"] = True
        result = generate_assessment_node(updated)
        updated.update(result)

    updated["log"] = state.get("log", []) + ["[HM Decision] Approved from review queue"]
    save_agent_state(app_id, updated)
    st.session_state["active_application_id"] = app_id