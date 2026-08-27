import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


s3_client = None

async def init_s3_client():
    try:
        global s3_client
        if s3_client is None:
            localstack_config = Config(
                region_name=settings.LOCALSTACK_REGION_NAME,
                retries={
                    "max_attempts": 3,
                    "mode": "standard"
                }
            )
            s3_client = boto3.client(
                service_name="s3",
                endpoint_url=settings.LOCALSTACK_HOST,
                aws_access_key_id=settings.LOCALSTACK_ACCESS_KEY,
                aws_secret_access_key=settings.LOCALSTACK_SECRET_ACCESS_KEY,
                config=localstack_config
            )
            logger.info("Localstack S3 client initialized successfully")
        return s3_client
    except Exception as e:
        logger.error(f"Error initializing localstack S3 client: {e}")
        raise e

async def close_s3_client():
    try:
        global s3_client
        if s3_client is not None:
            s3_client.close()
            del s3_client
            logger.info("Localstack S3 client closed successfully")
    except Exception as e:
        logger.error(f"Error closing localstack S3 client: {e}")
        raise e

async def get_s3_bucket():
    # Create bucket if it doesn't exist
    try:
        global s3_client
        if s3_client is not None:
            s3_client.create_bucket(Bucket=settings.S3_BUCKET_NAME)
            logger.info(f"S3 bucket {settings.S3_BUCKET_NAME} created successfully")
        else:
            raise Exception("S3 client not initialized")
    except Exception as e:
        logger.error(f"Error creating S3 bucket: {e}")
        raise e
