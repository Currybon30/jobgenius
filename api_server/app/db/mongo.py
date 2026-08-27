import logging
from pymongo import AsyncMongoClient
from app.core.config import settings

mongo_client: AsyncMongoClient | None = None

logger = logging.getLogger(__name__)

async def init_mongo():
    global mongo_client
    mongo_client = AsyncMongoClient(settings.MONGODB_URI)
    await mongo_client.admin.command("ping")
    logger.info("Mongo client initialized and connected successfully")


async def close_mongo():
    global mongo_client
    if mongo_client is not None:
        await mongo_client.close()
        del mongo_client
        logger.info("Mongo client closed successfully")

def get_mongo_client() -> AsyncMongoClient:
    if mongo_client is None:
        raise RuntimeError("Mongo client not initialized")
    return mongo_client