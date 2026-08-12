import logging
from fastapi import (
    APIRouter,
)
from fastapi.responses import JSONResponse
from app.helpers.auth_helper import is_premium_user
from app.services.job_service import search_jobs
