import pytest

from app.ai_agents.free_tier_multiagents import build_free_tier_graph
from app.core.ollama_config import close_ollama, init_ollama

RESUME_TEXT_SAMPLE = """
I am a software engineer with 5 years of experience in developing web applications using React, Node.js, and MongoDB. I have a strong understanding of the software development lifecycle and am able to work independently and as part of a team.
"""


@pytest.fixture
async def ollama():
    await init_ollama()
    yield
    await close_ollama()


@pytest.mark.asyncio
async def test_free_tier_graph_ainvoke(ollama):
    graph = await build_free_tier_graph()
    state = {
        "resume_text": RESUME_TEXT_SAMPLE,
        "jd_text": "",
        "user_goal": "",
    }

    result = await graph.ainvoke(state)

    assert "intent" in result
    assert "analyzer" in result
    assert "ats" in result
    assert "feedback" in result

    assert isinstance(result["intent"], dict)
    assert isinstance(result["analyzer"], dict)
    assert isinstance(result["ats"], dict)
    assert isinstance(result["feedback"], dict)

    assert "hard_skills" in result["analyzer"]
    assert "soft_skills" in result["analyzer"]
    assert "resume_score" in result["ats"]
    assert "section_score" in result["ats"]
