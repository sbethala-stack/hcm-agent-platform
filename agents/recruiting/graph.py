from langgraph.graph import StateGraph, END
from agents.recruiting.state import RecruitingState
from agents.recruiting.nodes import (
    extract_candidate_node,
    match_resume_node,
    route_after_match,
    human_review_queue_node,
    generate_assessment_node,
    score_assessment_node,
    route_after_assessment,
    schedule_interview_node,
    error_node,
)


def build_recruiting_graph():
    graph = StateGraph(RecruitingState)

    graph.add_node("extract_candidate", extract_candidate_node)
    graph.add_node("match_resume", match_resume_node)
    graph.add_node("human_review_queue", human_review_queue_node)
    graph.add_node("generate_assessment", generate_assessment_node)
    graph.add_node("score_assessment", score_assessment_node)
    graph.add_node("schedule_interview", schedule_interview_node)
    graph.add_node("error", error_node)

    graph.set_entry_point("extract_candidate")

    graph.add_edge("extract_candidate", "match_resume")

    graph.add_conditional_edges(
        "match_resume",
        route_after_match,
        {
            "generate_assessment": "generate_assessment",
            "human_review_queue": "human_review_queue",
            "error": "error",
        }
    )

    graph.add_edge("generate_assessment", END)
    graph.add_edge("human_review_queue", END)

    graph.add_conditional_edges(
        "score_assessment",
        route_after_assessment,
        {
            "schedule_interview": "schedule_interview",
            "human_review_queue": "human_review_queue",
            "error": "error",
        }
    )

    graph.add_edge("schedule_interview", END)
    graph.add_edge("error", END)

    return graph.compile()


recruiting_graph = build_recruiting_graph()