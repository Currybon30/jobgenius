import logging
from pinecone import AsyncPinecone, ServerlessSpec
from app.core.config import settings

pinecone_client: AsyncPinecone | None = None
pinecone_index = None

logger = logging.getLogger(__name__)

async def init_pinecone():
    global pinecone_client, pinecone_index
    pinecone_client = AsyncPinecone(api_key=settings.PINECONE_API_KEY, 
                                    host=settings.PINECONE_HOST)
    
    index_name = settings.PINECONE_INDEX_NAME
    if not await pinecone_client.has_index(index_name):
        index_model = await pinecone_client.create_index(
            name=index_name,
            vector_type="dense",
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            ),
            deletion_protection='disabled', # TODO: Change to True in production
            tags={"environment": "development"},  # TODO: Change to production environment
        )
        logger.info(f"Pinecone index {index_model} created successfully")
    else:
        logger.info(f"Pinecone index {index_name} already exists")
    
    index_info = await pinecone_client.describe_index(index_name)
    host = index_info.host
    if not host.startswith(("https://", "http://")):
        host = f"http://{host}"
    elif host.startswith("https://"):
        # Local only: force http
        host = "http://" + host.removeprefix("https://")
    pinecone_index = pinecone_client.IndexAsyncio(
        host=host,
        ssl_verify=False
    )
    try:
        await pinecone_index.describe_index_stats()
        logger.info(f"Pinecone index {index_name} is ready")
    except Exception as e:
        logger.error(f"Error describing Pinecone index {index_name}: {e}")
        raise e


async def close_pinecone():
    global pinecone_client, pinecone_index
    if pinecone_client is not None:
        await pinecone_client.close()
        pinecone_client = None
        pinecone_index = None
        logger.info("Pinecone client closed successfully")

def get_pinecone_client() -> AsyncPinecone:
    if pinecone_client is None:
        raise RuntimeError("Pinecone client not initialized")
    return pinecone_client

def get_pinecone_index():
    if pinecone_index is None:
        raise RuntimeError("Pinecone index not initialized")
    return pinecone_index