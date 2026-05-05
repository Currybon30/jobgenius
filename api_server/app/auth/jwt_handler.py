import jwt
from app.core.config import settings
from fastapi import HTTPException, status


def decode_jwt(access_token: str):
    try:
        payload = jwt.decode(access_token, settings.JWT_SECRET_KEY, algorithms=[
                             settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
