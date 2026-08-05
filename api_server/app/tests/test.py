from app.ai_agents.free_tier_multiagents import build_free_tier_graph
from IPython.display import Image, display
import asyncio

async def test_main():
    graph = await build_free_tier_graph()
    resume_text_sample = """
    I am a software engineer with 5 years of experience in developing web applications using React, Node.js, and MongoDB. I have a strong understanding of the software development lifecycle and am able to work independently and as part of a team.
    """
    jd_text_sample = """
    We are looking for a software engineer with 5 years of experience in developing web applications using React, Node.js, and MongoDB.
    """
    user_goal_sample = """
    I am looking for a software engineer with 5 years of experience in developing web applications using React, Node.js, and MongoDB.
    """
    state = {"resume_text": resume_text_sample, "jd_text": jd_text_sample, "user_goal": user_goal_sample}
    result = await graph.ainvoke(state)
    print(result)


asyncio.run(test_main())


