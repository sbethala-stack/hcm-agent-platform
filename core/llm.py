from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config.settings import get_settings
import json
import re


def get_llm():
    settings = get_settings()
    return ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.llm_model,
        temperature=settings.llm_temperature,
    )


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
)
def call_llm(system_prompt: str, user_prompt: str) -> str:
    llm = get_llm()
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]
    response = llm.invoke(messages)
    return response.content


def call_llm_json(system_prompt: str, user_prompt: str) -> dict:
    raw = call_llm(
        system_prompt,
        user_prompt + "\n\nRespond ONLY with valid JSON. No preamble, no markdown fences."
    )
    cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
    return json.loads(cleaned)