from app.core.config import settings
from app.db.pinecone import get_pinecone_index
from app.helpers.job_api_helper import jsearch_format_data, jsearch_json_to_text
from app.services.resume_service import get_resume_for_job_recommendation_from_mongodb
from app.helpers.embedding_helper import embed_text
from app.db.mongo import get_mongo_client
import niquests
import logging
from typing import List, Optional
from fastmcp import FastMCP
from app.models.job import Job

logger = logging.getLogger(__name__)
mcp = FastMCP("job_service")


@mcp.tool("search_jobs", 
    description="""
    Search jobs through the third-party API (JSearch API)
    Parameters:
        query: The query to search for jobs
        country: The country to search for jobs (if given) - Default values: ca
        language: The language to search for jobs (if given) - Default values: en
        date_posted: Date posted (if given) - Default values: all, today, 3days, week, month
        employment_types (optional): Employment types (if given) - Default values: FULLTIME, CONTRACTOR, PARTTIME, INTERN
    Returns:
        A list of jobs in JSON format
    """)
async def search_jobs(query: str, country: str = "ca", language: str = "en", date_posted: str = "all", employment_types: Optional[List[str]] = None):
    params = {
        "query": query,
        "num_pages": 3,
        "country": country,
        "language": language,
        "date_posted": date_posted or "all"
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


async def _store_jobs_to_mongodb(job_data, json_to_text: str, pinecone_id: Optional[str] = None, model: Optional[str] = None):
    mongo_client = get_mongo_client()
    mongo_db = mongo_client[settings.MONGODB_NAME]
    jobs_collection = mongo_db["jobs"]
    job = jsearch_format_data(job_data, json_to_text, pinecone_id, model)
    await jobs_collection.update_one(
        {"id": job["id"], "source": job["source"]},
        {"$set": job},
        upsert=True,
    )

async def get_job_from_mongodb(job_id: str) -> dict:
    mongo_client = get_mongo_client()
    mongo_db = mongo_client[settings.MONGODB_NAME]
    jobs_collection = mongo_db["jobs"]
    job = await jobs_collection.find_one({"id": job_id})
    if not job:
        return None
    return Job.model_validate(job).model_dump()

def _pinecone_job_metadata(job_data: dict) -> dict:
    return {
        k: v
        for k, v in {
            "job_id": job_data.get("job_id"),
            "employer_name": job_data.get("employer_name"),
            "job_country": job_data.get("job_country")
        }.items()
        if v is not None
    }


async def store_jobs_to_pinecone(data):
    """
    Store searched jobs from JSearch API to Pinecone, also store to MongoDB simultaneously
    Parameters:
        data: A list of jobs in JSON format from JSearch API
    Returns:
        True if all jobs are stored to MongoDB and Pinecone successfully, False otherwise
    """
    try:
        pinecone_index = get_pinecone_index()
        for job_data in data:
            job_id = job_data.get("job_id")
            if not job_id:
                logger.warning("Skipping job without job_id")
                continue

            pinecone_id = "vec" + job_id
            if pinecone_index.fetch(ids=[pinecone_id]):
                logger.warning(f"Job {job_id} already exists in Pinecone")
                continue
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
                await _store_jobs_to_mongodb(
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

async def search_jobs_in_pinecone(query: str) -> List[dict]:
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
        matches = results.get("matches", [])
        if not matches:
            return []

        return matches
    except Exception as e:
        logger.error(f"Error getting jobs in Pinecone: {e}")
        return []

async def job_recommendation(resume_id: str) -> dict:
    try:
        resume = await get_resume_for_job_recommendation_from_mongodb(resume_id)
        if not resume:
            return {"error": "Resume not found"}
        resume_text = resume.get("full_combined_text") or ""
        if not resume_text.strip():
            return {"error": "Resume has no searchable text"}
        matches = await search_jobs_in_pinecone(resume_text)
        if not matches:
            return {"error": "No jobs found"}
        matches = [m for m in matches if m.get("score", 0) > 0.65]
        if not matches:
            return {"error": "No jobs above similarity threshold"}
        recommended_jobs = []
        for match in matches:
            job_id = (match.get("metadata") or {}).get("job_id")
            if not job_id:
                continue
            job = await get_job_from_mongodb(job_id)
            if job and job.get("is_active", True):
                recommended_jobs.append({"job": job, "score": match["score"]})
        return recommended_jobs
    except Exception as e:
        logger.error(f"Error getting job recommendation: {e}")
        return []