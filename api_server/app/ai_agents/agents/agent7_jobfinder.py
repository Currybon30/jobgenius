import json
from fastapi import BackgroundTasks
from langchain_core.messages import ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient 
from langchain_ollama import ChatOllama
from app.services.job_service import store_jobs_to_pinecone
from langchain.agents import create_agent
from app.core.config import settings

async def jobfinder_agent(background_tasks: BackgroundTasks, resume_text: str, analyzed_results_dict: dict = None, user_requirements: str = ""):
    mcp_client = MultiServerMCPClient({
    "job_service": {
        "command": "python",
        "args": ["-m", "app.mcp.job_mcp"],
        "transport": "stdio"
        }
    })
    
    tools = await mcp_client.get_tools()

    model = ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_HOST,
    )

    agent = create_agent(
        model=model,
        tools=tools
    )

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
            """
        }
    ]

    if analyzed_results_dict:
        messages.append({
            "role": "user",
            "content": f"""
                Original resume text: {resume_text}
                Analyzed results dictionary: {analyzed_results_dict}
            """
        })
    else:
        messages.append({
            "role": "user",
            "content": f"""
                Original resume text: {resume_text}
                User requirements: {user_requirements}
            """
        })

    result = await agent.ainvoke({
        "messages": messages
    })

    for msg in result["messages"]:
        if isinstance(msg, ToolMessage):
            if isinstance(msg.content, list):
                background_tasks.add_task(store_jobs_to_pinecone, msg.content)
            else:
                jobs = []
                parsed = json.loads(msg.content) if isinstance(msg.content, str) else msg.content
                jobs.extend(parsed)
                background_tasks.add_task(store_jobs_to_pinecone, jobs)

    messages.append({
        "role": "assistant",
        "content": result["messages"][-1].content
    })

    messages.append({
        "role": "user",
        "content": f"""
            Explain why these jobs are the best fit for the user based on the original resume text and the analyzed results dictionary or user requirements.
            Be concise and to the point.
            Use bullet points to list the reasons if it is appropriate.
        """
    })

    result = await agent.ainvoke({
        "messages": messages
    })

    messages.append({
        "role": "assistant",
        "content": result["messages"][-1].content
    })

    return messages