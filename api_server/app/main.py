from fastapi import FastAPI
from app.db.base import Base
from app.core.config import settings
from app.middlewares.timing import timing_middleware
from app.middlewares.logging import logging_middleware
from app.core.logging_config import setup_logging
from app.routes.user_router import router as user_router
from app.db.session import engine

setup_logging()

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

# Remember to setup security dependencies and CORS middleware as needed

app.include_router(user_router)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

app.middleware("http")(timing_middleware)
app.middleware("http")(logging_middleware)