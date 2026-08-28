import asyncio
import logging

from bson import ObjectId

from app.core.config import settings
from app.db.mongo import get_mongo_client
from app.helpers.resume_helper import analyzer_result_to_text, format_analyzer_result
from app.models.resume import Resume, ResumeForJobRecommendation
from app.db.s3 import get_s3_client

logger = logging.getLogger(__name__)


def _resume_to_mongo(resume: Resume) -> dict:
    document = resume.model_dump()
    document["_id"] = document.pop("id")
    return document


async def store_resume_to_mongodb(user_id: int, resume, analyzed_result: dict):
    try:
        s3_client = await get_s3_client()
        mongo_client = get_mongo_client()
        mongo_db = mongo_client[settings.MONGODB_NAME]
        resume_collection = mongo_db["resumes"]
        resume_for_job_recommendation_collection = mongo_db["resume_for_job_recommendation"]

        formatted_result = format_analyzer_result(analyzed_result)
        full_combined_text = analyzer_result_to_text(analyzed_result)
        resume_id_generator = f"{user_id}_{resume.filename}"

        existing_resume = await resume_collection.find_one(
            {"resume_id": resume_id_generator},
            sort=[("version", -1)],
        )
        next_version = (existing_resume["version"] + 1) if existing_resume else 1

        await asyncio.to_thread(
            s3_client.upload_file,
            Filename=resume.filename,
            Bucket=settings.S3_BUCKET_NAME,
            Key=f"{user_id}/{resume.filename}/{next_version}.pdf",
            ExtraArgs={
                "ContentType": "application/pdf",
                "ContentDisposition": "inline",
            },
        )

        new_resume = Resume(
            id=ObjectId(),
            user_id=user_id,
            resume_id=resume_id_generator,
            version=next_version,
            filename=resume.filename,
            storage_path=f"{user_id}/{resume.filename}/{next_version}.pdf",
            analysis=formatted_result,
        )
        await resume_collection.insert_one(_resume_to_mongo(new_resume))

        existing_recommendation = await resume_for_job_recommendation_collection.find_one(
            {"resume_id": resume_id_generator}
        )
        if existing_recommendation is None:
            recommendation = ResumeForJobRecommendation(
                user_id=user_id,
                resume_id=resume_id_generator,
                version=next_version,
                full_combined_text=full_combined_text,
            )
            await resume_for_job_recommendation_collection.insert_one(
                recommendation.model_dump(mode="json")
            )
        else:
            await resume_for_job_recommendation_collection.update_one(
                {"resume_id": resume_id_generator},
                {
                    "$set": {
                        "user_id": user_id,
                        "full_combined_text": full_combined_text,
                        "version": next_version,
                    }
                },
            )

        return True
    except Exception as e:
        logger.error(f"Error storing resume to MongoDB: {e}")
        return False


async def get_resumes_from_mongodb(user_id: int):
    try:
        mongo_client = get_mongo_client()
        mongo_db = mongo_client[settings.MONGODB_NAME]
        resume_collection = mongo_db["resumes"]
        responses = await resume_collection.find({"user_id": user_id})

        # Return indicated keys to user
        resumes = []
        for response in responses:
            resumes.append({
                "resume_id": response["resume_id"],
                "version": response["version"],
                "filename": response["filename"],
                "storage_path": response["storage_path"]
            })
        return resumes
    except Exception as e:
        logger.error(f"Error getting resume from MongoDB: {e}")
        return []

async def get_resume_by_id_and_version_from_mongodb(resume_id: str, version: int):
    try:
        mongo_client = get_mongo_client()
        mongo_db = mongo_client[settings.MONGODB_NAME]
        resume_collection = mongo_db["resumes"]
        response = await resume_collection.find_one({"resume_id": resume_id, "version": version})
        if response is None:
            return None
        return {
            "resume_id": response["resume_id"],
            "version": response["version"],
            "filename": response["filename"],
            "storage_path": response["storage_path"],
            "analysis": response["analysis"]
        }
    except Exception as e:
        logger.error(f"Error getting resume by id and version from MongoDB: {e}")
        return None


async def get_resume_for_job_recommendation_from_mongodb(resume_id: str):
    try:
        mongo_client = get_mongo_client()
        mongo_db = mongo_client[settings.MONGODB_NAME]
        resume_for_job_recommendation_collection = mongo_db["resume_for_job_recommendation"]
        return await resume_for_job_recommendation_collection.find_one({"resume_id": resume_id})
    except Exception as e:
        logger.error(f"Error getting resume for job recommendation from MongoDB: {e}")
        return None
