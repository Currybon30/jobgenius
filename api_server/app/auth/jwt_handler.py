import jwt
from app.core.config import settings
from fastapi import HTTPException, status
import logging


logger = logging.getLogger(__name__)


def decode_jwt(access_token: str):
    try:
        payload = jwt.decode(access_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.info("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        logger.info("Invalid token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
