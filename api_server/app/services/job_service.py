# Show random jobs from Job API for unlogged-in users, matching the user's location and industry
# If the user logged in and is a free user, show jobs matching the user's location, industry and job title
# If the user logged in and is a premium user, show jobs matching the user's location, industry, job title, job level, etc.
from app.core.config import settings
from app.db.pinecone import get_pinecone_index
from app.helpers.job_api_helper import jsearch_format_data, jsearch_json_to_text
from app.helpers.embedding_helper import embed_text
from app.db.mongo import get_mongo_client
import niquests
import logging
from typing import List, Optional
from fastmcp import FastMCP

logger = logging.getLogger(__name__)
mcp = FastMCP("job_service")


@mcp.tool("search_jobs_canada", 
    description="""
    Search jobs in Canada through the third-party API (JSearch API)
    Parameters:
        query: The query to search for jobs
        date_posted (optional): Date posted (if given) - Default values: all, today, 3days, week, month
        employment_types (optional): Employment types (if given) - Default values: FULLTIME, CONTRACTOR, PARTTIME, INTERN
    Returns:
        A list of jobs in JSON format
    """)
async def search_jobs_canada(query: str, date_posted: str = "all", employment_types: Optional[List[str]] = None):
    params = {
        "query": query,
        "num_pages": 3,
        "country": "ca",
        "language": "en",
        "date_posted": date_posted or "all",
    }
    if employment_types:
        params["employment_types"] = ",".join(employment_types)

    response = await niquests.aget(
        f"{settings.JSEARCH_HOST}/search-v2",
        headers=settings.JSEARCH_HEADERS,
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    body = response.json()

    if body.get("status") != "OK":
        logger.error("JSearch request failed: %s", body)
        raise RuntimeError(f"Failed to search jobs: {body.get('status')}")

    data = body.get("data") or {}
    return data.get("jobs", [])


async def store_jobs_to_mongodb(job_data, json_to_text: str, pinecone_id: Optional[str] = None, model: Optional[str] = None):
    mongo_client = get_mongo_client()
    mongo_db = mongo_client[settings.MONGODB_NAME]
    jobs_collection = mongo_db["jobs"]
    job = jsearch_format_data(job_data, json_to_text, pinecone_id, model)
    await jobs_collection.update_one(
        {"id": job["id"], "source": job["source"]},
        {"$set": job},
        upsert=True,
    )


def _pinecone_job_metadata(job_data: dict) -> dict:
    return {
        k: v
        for k, v in {
            "job_id": job_data.get("job_id"),
            "job_title": job_data.get("job_title"),
            "employer_name": job_data.get("employer_name"),
            "job_city": job_data.get("job_city"),
            "job_state": job_data.get("job_state"),
            "job_country": job_data.get("job_country"),
            "job_apply_link": job_data.get("job_apply_link"),
        }.items()
        if v is not None
    }


async def store_jobs_to_pinecone(data):
    try:
        pinecone_index = get_pinecone_index()
        for job_data in data:
            job_id = job_data.get("job_id")
            if not job_id:
                logger.warning("Skipping job without job_id")
                continue

            pinecone_id = "vec" + job_id
            json_to_text = jsearch_json_to_text(job_data)
            embedding = await embed_text(json_to_text)
            if not embedding:
                logger.error(f"Empty embedding for job {job_id}")
                continue

            await pinecone_index.upsert(
                vectors=[
                    {
                        "id": pinecone_id,
                        "values": embedding,
                        "metadata": _pinecone_job_metadata(job_data),
                    }
                ],
                namespace="jobs",
            )
            try:
                await store_jobs_to_mongodb(
                    job_data,
                    json_to_text,
                    pinecone_id,
                    settings.EMBEDDING_MODEL_NAME,
                )
            except Exception as e:
                logger.error(f"Error storing job {job_id} to MongoDB: {e}")
                continue
        logger.info("All jobs stored to MongoDB and Pinecone successfully")
        return True
    except Exception as e:
        logger.error(f"Error storing jobs to MongoDB and Pinecone: {e}")
        return False

async def get_jobs_in_pinecone(query: str) -> List[dict]:
    try:
        pinecone_index = get_pinecone_index()
        embedding = await embed_text(query)
        if not embedding:
            return []

        results = await pinecone_index.query(
            vector=embedding,
            top_k=10,
            namespace="jobs",
        )
        matches = getattr(results, "matches", None)
        if matches is None and isinstance(results, dict):
            matches = results.get("matches", [])

        normalized_matches = []
        for match in matches or []:
            if hasattr(match, "model_dump"):
                normalized_matches.append(match.model_dump())
            elif isinstance(match, dict):
                normalized_matches.append(match)
            else:
                normalized_matches.append(dict(match))
        return normalized_matches
    except Exception as e:
        logger.error(f"Error getting jobs in Pinecone: {e}")
        return []

async def job_recommendation(resume_id: str, job_id: str) -> dict:
    pass