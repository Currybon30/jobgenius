from app.ai_agents.premium_multiagents import jobfinder_agent
from app.helpers.llm_call import agent7_jobfinder_format_result
import pymupdf
from pathlib import Path

async def test_agent_jobfinder():
    pdf_bytes = Path(r"D:\IT\My Projects\job_recommender_system\api_server\external\Tuong_Nguyen_Pham_Resume.pdf").read_bytes()
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text() # type: ignore
    doc.close()
    user_requirements = "I am looking for a job as a software engineer without any experience, I have only some projects, volunteering extracurricular activities, and some courses. I am looking for a job around the world."
    messages, raw_jobs = await jobfinder_agent(resume_text=text, user_requirements=user_requirements)
    jobfinder_result = agent7_jobfinder_format_result(messages, raw_jobs)
    explanation_message = jobfinder_result["message"]
    jobs = jobfinder_result["jobs"]
    print(explanation_message)
    print(jobs)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_agent_jobfinder())