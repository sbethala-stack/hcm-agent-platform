import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="HCM Agent Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("HCM Agent Platform")
st.sidebar.caption("AI-powered Human Capital Management")
st.sidebar.divider()

module = st.sidebar.selectbox(
    "Module",
    ["Recruiting"],
    help="More HCM modules coming soon"
)

if module == "Recruiting":
    page = st.sidebar.radio(
        "Page",
        ["Resume Screening", "Review Queue", "Application Tracker"]
    )

st.sidebar.divider()
st.sidebar.caption("ERP Layer: Mock (Oracle HCM shape)")
st.sidebar.caption("LLM: Groq / Llama 3 70B")
st.sidebar.caption("Orchestration: LangGraph")

if module == "Recruiting":
    if page == "Resume Screening":
        from ui.recruiting.upload import render_upload_page
        render_upload_page()
    elif page == "Review Queue":
        from ui.recruiting.review_queue import render_review_queue
        render_review_queue()
    elif page == "Application Tracker":
        from ui.recruiting.tracker import render_tracker
        render_tracker()