import logging

from app.auth.jwt_handler import decode_jwt
from fastapi import HTTPException, Request, status

logger = logging.getLogger(__name__)


def get_current_user_id(request: Request) -> int:
    access_token = request.cookies.get("access_token")
    if not access_token:
        logger.warning("Access token is missing")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token is missing"
        )

    payload = decode_jwt(access_token)
    user_id = payload.get("user_id")

    if user_id is None:
        logger.warning("Invalid token payload")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )

    return int(user_id)
