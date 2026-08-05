from typing import Any, Optional, TypedDict

from langgraph.graph import StateGraph, START, END

from app.ai_agents.agents.agent1_intent import intent_goal_agent
from app.ai_agents.agents.agent2_analyzer import analyzer_agent_free_tier
from app.ai_agents.agents.agent3_ats import ats_agent_free_tier
from app.ai_agents.agents.agent6_finalizer import finalizer_agent_free_tier


class GraphState(TypedDict, total=False):
    # User input states
    resume_text: str
    jd_text: Optional[str]
    user_goal: Optional[str]

    # Agent output states
    intent: dict[str, Any] | Any
    analyzer: dict[str, Any]
    ats: dict[str, Any]
    feedback: dict[str, Any] | str


async def agent1_node(state: GraphState) -> GraphState:
    intent = await intent_goal_agent(
        state["resume_text"],
        state.get("jd_text"),
        state.get("user_goal"),
    )
    return {"intent": intent}


async def agent2_node(state: GraphState) -> GraphState:
    industry = state.get("intent", {}).get("industry")
    analyzer = analyzer_agent_free_tier(
        state["resume_text"],
        industry,
        state.get("jd_text"),
    )
    return {"analyzer": analyzer}


async def agent3_node(state: GraphState) -> GraphState:
    ats = ats_agent_free_tier(state["analyzer"])
    return {"ats": ats}


async def agent6_node(state: GraphState) -> GraphState:
    feedback = await finalizer_agent_free_tier(
        resume_text=state["resume_text"],
        intent=state.get("intent") or {},
        analyzer=state.get("analyzer") or {},
        ats=state.get("ats") or {},
        user_goal=state.get("user_goal"),
    )
    return {"feedback": feedback}


async def build_free_tier_graph():
    graph = StateGraph(GraphState)
    graph.add_node("agent1_intent", agent1_node)
    graph.add_node("agent2_analyzer", agent2_node)
    graph.add_node("agent3_ats", agent3_node)
    graph.add_node("agent6_finalizer", agent6_node)
    graph.add_edge(START, "agent1_intent")
    graph.add_edge("agent1_intent", "agent2_analyzer")
    graph.add_edge("agent2_analyzer", "agent3_ats")
    graph.add_edge("agent3_ats", "agent6_finalizer")
    graph.add_edge("agent6_finalizer", END)
    return graph.compile()