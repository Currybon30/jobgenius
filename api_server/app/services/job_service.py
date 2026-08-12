# Show random jobs from Job API for unlogged-in users, matching the user's location and industry
# If the user logged in and is a free user, show jobs matching the user's location, industry and job title
# If the user logged in and is a premium user, show jobs matching the user's location, industry, job title, job level, etc.
from app.core.config import settings
import niquests
import logging
from typing import List, Optional
from langchain.agents import tool

logger = logging.getLogger(__name__)

@tool("search_jobs_canada", 
    description="""
    Search jobs in Canada through the third-party API (JSearch API)
    Args:
        query: The query to search for jobs
        What should be included in the query?
        - Job title
        - City in Canada
        date_posted (optional): Date posted (if given) - Default values: all, today, 3days, week, month
        employment_types (optional): Employment types (if given) - Default values: FULLTIME, CONTRACTOR, PARTTIME, INTERN
    Returns:
        A list of jobs in JSON format
    """)
async def search_jobs(query: str, date_posted: str = "all", employment_types: Optional[List[str]] = None):
    if employment_types:
        employment_types = ",".join(employment_types)

    payload = {
        "query": query,
        "page": 5,
        "country": "ca",
        "language": "en",
        "employment_types": employment_types if employment_types else "",
        "date_posted": date_posted if date_posted else "all"
    }

    response = await niquests.aget(
        url=f"{settings.JSEARCH_HOST}/search-v2",
        headers=settings.JSEARCH_HEADERS,
        params=payload,
    )
    if not response.status == "OK":
        raise Exception(f"Failed to search jobs: {response.status}")
    data = response.get("data")
    return data