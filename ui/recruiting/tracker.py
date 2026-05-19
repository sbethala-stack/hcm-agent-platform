import streamlit as st
from core.models import ApplicationStatus
from ui.session import get_agent_states

STATUS_EMOJI = {
    ApplicationStatus.RECEIVED.value: "📥",
    ApplicationStatus.SCREENING.value: "🔍",
    ApplicationStatus.HUMAN_REVIEW.value: "👤",
    ApplicationStatus.ASSESSMENT_SENT.value: "📝",
    ApplicationStatus.ASSESSMENT_SCORED.value: "📊",
    ApplicationStatus.INTERVIEW_SCHEDULED.value: "📅",
    ApplicationStatus.REJECTED.value: "❌",
    ApplicationStatus.OFFER_PENDING.value: "📬",
}


def render_tracker():
    st.title("Application Tracker")
    st.caption("Full pipeline overview of all applications this session")

    states = get_agent_states()

    if not states:
        st.info("No applications submitted yet. Go to Resume Screening to get started.")
        return

    total = len(states)
    by_status = {}
    for s in states.values():
        status = s.get("status", "received")
        by_status[status] = by_status.get(status, 0) + 1

    cols = st.columns(5)
    metrics = [
        ("Total", total),
        ("In Review", by_status.get(ApplicationStatus.HUMAN_REVIEW.value, 0)),
        ("Assessment", by_status.get(ApplicationStatus.ASSESSMENT_SENT.value, 0)),
        ("Interview", by_status.get(ApplicationStatus.INTERVIEW_SCHEDULED.value, 0)),
        ("Rejected", by_status.get(ApplicationStatus.REJECTED.value, 0)),
    ]
    for col, (label, val) in zip(cols, metrics):
        with col:
            st.metric(label, val)

    st.divider()

    for app_id, state in states.items():
        cand = state.get("candidate", {})
        req = state.get("requisition", {})
        match = state.get("match_result", {})
        asmt = state.get("assessment_score")
        status = state.get("status", "received")
        emoji = STATUS_EMOJI.get(status, "❓")

        with st.container(border=True):
            col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 2])
            with col1:
                st.markdown(f"**{cand.get('name', app_id)}**")
                st.caption(f"{cand.get('current_title', '—')} | {cand.get('years_of_experience', '—')} yrs")
            with col2:
                st.write(req.get("title", "—"))
                st.caption(req.get("department", "—"))
            with col3:
                score = match.get("score")
                if score is not None:
                    st.metric("Match", f"{score:.0f}%", label_visibility="collapsed")
            with col4:
                if asmt:
                    asmt_s = asmt.get("overall_score")
                    st.metric("Asmt", f"{asmt_s:.0f}%", label_visibility="collapsed")
            with col5:
                st.markdown(f"{emoji} `{status.replace('_', ' ').title()}`")
                st.caption(app_id)