from app.core.config import settings
from app.core.logging_config import setup_logging
from app.db.base import Base
from app.db.redis import close_redis, init_redis
from app.db.session import engine
from app.middlewares.limit import rate_limit_middleware
from app.middlewares.logging import logging_middleware
from app.middlewares.timing import timing_middleware
from app.routes.resume_router import router as resume_router
from app.routes.user_router import router as user_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

setup_logging()

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


app.include_router(user_router)
app.include_router(resume_router)


@app.on_event("startup")
async def on_startup():
    await init_redis()
    Base.metadata.create_all(bind=engine)


@app.on_event("shutdown")
async def on_shutdown():
    await close_redis()


@app.get("/health")
async def health_check():
    return {"status": "ok"}

app.middleware("http")(logging_middleware)
app.middleware("http")(rate_limit_middleware)
app.middleware("http")(timing_middleware)
