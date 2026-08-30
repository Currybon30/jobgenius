import pytest

from app.ai_agents.free_tier_multiagents import build_free_tier_graph

RESUME_TEXT_SAMPLE = """
I am a software engineer with 5 years of experience in developing web applications using React, Node.js, and MongoDB. I have a strong understanding of the software development lifecycle and am able to work independently and as part of a team.
"""

JD_TEXT_SAMPLE = """
We are looking for a software engineer with 5 years of experience in developing web applications using React, Node.js, and MongoDB.
"""


@pytest.mark.asyncio
async def test_free_tier_graph_ainvoke():
    graph = await build_free_tier_graph()
    state = {
        "resume_text": RESUME_TEXT_SAMPLE,
        "jd_text": JD_TEXT_SAMPLE,
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


    # check intent agent response
    assert "target_role" in result["intent"]
    assert "seniority_level" in result["intent"]
    assert "industry" in result["intent"]
    assert "priority_goals" in result["intent"]
    assert "focus_areas" in result["intent"]
    assert "top_keywords" in result["intent"]
    assert "optimization_strategy" in result["intent"]

    # check analyzer agent response
    assert "sections" in result["analyzer"]
    assert "years_exp" in result["analyzer"]
    assert "has_summary" in result["analyzer"]
    assert "has_skills" in result["analyzer"]
    assert "has_experience" in result["analyzer"]
    assert "has_projects" in result["analyzer"]
    assert "has_education" in result["analyzer"]
    assert "emails" in result["analyzer"]
    assert "phone_numbers" in result["analyzer"]
    assert "has_metrics" in result["analyzer"]
    assert "hard_skills" in result["analyzer"]
    assert "soft_skills" in result["analyzer"]
    if JD_TEXT_SAMPLE != "":
        assert "missing_hard_skills" in result["analyzer"]
        assert "matching_hard_skills_score" in result["analyzer"]
        assert "missing_soft_skills" in result["analyzer"]
        assert "matching_soft_skills_score" in result["analyzer"]

    # check ats agent response
    assert "resume_score" in result["ats"]
    assert "section_score" in result["ats"]
    assert "experience_projects_score" in result["ats"]
    assert "skills_quality_score" in result["ats"]
    assert "summary_quality_score" in result["ats"]
    assert "formatting_score" in result["ats"]
    if JD_TEXT_SAMPLE != "":
        assert "ats_score" in result["ats"]
        assert "hard_skills_score" in result["ats"]
        assert "soft_skills_score" in result["ats"]

    # check finalizer agent response
    assert "summary" in result["feedback"]
    assert "skills_feedback" in result["feedback"]
    assert "experience_feedback" in result["feedback"]
    assert "structure_feedback" in result["feedback"]
    assert "simple_suggestions" in result["feedback"]