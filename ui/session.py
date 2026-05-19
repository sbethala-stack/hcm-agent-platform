import streamlit as st
from connectors.factory import get_erp_connector
from connectors.base import BaseERPConnector


def get_erp() -> BaseERPConnector:
    if "erp_connector" not in st.session_state:
        st.session_state["erp_connector"] = get_erp_connector()
    return st.session_state["erp_connector"]


def get_agent_states() -> dict:
    if "agent_states" not in st.session_state:
        st.session_state["agent_states"] = {}
    return st.session_state["agent_states"]


def save_agent_state(application_id: str, state: dict):
    states = get_agent_states()
    states[application_id] = state
    st.session_state["agent_states"] = states


def get_agent_state(application_id: str) -> dict | None:
    return get_agent_states().get(application_id)