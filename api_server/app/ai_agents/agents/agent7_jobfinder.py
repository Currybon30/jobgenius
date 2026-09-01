import json

from app.core.config import settings
from app.helpers.job_indexing import index_jobs_in_background
from langchain.agents import create_agent
from langchain_core.messages import ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama


async def jobfinder_agent(
    resume_text: str,
    analyzed_results_dict: dict | None = None,
    user_requirements: str = "",
):
    mcp_client = MultiServerMCPClient(
        {
            "job_service": {
                "command": "python",
                "args": ["-m", "app.mcp.job_mcp"],
                "transport": "stdio",
            }
        }
    )

    tools = await mcp_client.get_tools()

    model = ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_HOST,
    )

    agent = create_agent(model=model, tools=tools)

    messages = [
        {
            "role": "system",
            "content": """
                You are a job finder agent. You are provided with an original resume text 
                An analyzed results dictionary from previous agents or user requirements are optional.
                Your task is to find the best jobs for the user based on the original resume text and the analyzed results dictionary or user requirements.
                You are also provided with a tool to search for jobs.
                Note that you need to self-analyze the input to determine the best jobs for the user.
                You must return the jobs with a beautiful and concise description of the job for later summary.
            """,
        }
    ]

    if analyzed_results_dict:
        messages.append(
            {
                "role": "user",
                "content": f"""
                Original resume text: {resume_text}
                Analyzed results dictionary: {analyzed_results_dict}
            """,
            }
        )
    else:
        messages.append(
            {
                "role": "user",
                "content": f"""
                Original resume text: {resume_text}
                User requirements: {user_requirements}
            """,
            }
        )

    result = await agent.ainvoke({"messages": messages})

    raw_jobs = None

    for msg in result["messages"]:
        if isinstance(msg, ToolMessage):
            if isinstance(msg.content, list):
                jobs = msg.content
                raw_jobs = jobs
                await index_jobs_in_background(jobs)
            else:
                parsed = (
                    json.loads(msg.content)
                    if isinstance(msg.content, str)
                    else msg.content
                )
                jobs = parsed if isinstance(parsed, list) else [parsed]
                raw_jobs = jobs
                await index_jobs_in_background(jobs)

    messages.append({"role": "assistant", "content": result["messages"][-1].content})

    messages.append(
        {
            "role": "user",
            "content": """
            Explain why these jobs are the best fit for the user based on the original resume text and the analyzed results dictionary or user requirements.
            Be concise and to the point.
            Use bullet points to list the reasons if it is appropriate.
        """,
        }
    )

    result = await agent.ainvoke({"messages": messages})

    messages.append({"role": "assistant", "content": result["messages"][-1].content})

    return messages, raw_jobs


# if __name__ == "__main__":
#     import asyncio
#     resume_text = """
#     I am a software engineer with 5 years of experience in Python and Django. I have a passion for building web applications and I am looking for a new challenge.
#     """
#     analyzed_results_dict = {
#         "skills": ["Python", "Django", "JavaScript", "React", "SQL"],
#         "experience": "5 years",
#         "education": "Bachelor of Science in Computer Science",
#         "location": "San Francisco, CA",
#         "job_type": "Full-time",
#         "job_category": "Software Engineering",
#     }
#     messages, raw_jobs = asyncio.run(jobfinder_agent(resume_text=resume_text, analyzed_results_dict=analyzed_results_dict))
#     print_results = ""
#     for msg in messages:
#         print_results += msg["role"] + ": " + msg["content"] + "\n"
#     print(raw_jobs)

#     with open("jobfinder_results.txt", "w") as f:
#         f.write(print_results)
