from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router, cards
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title="Kima's MTG Deck Builder API", version="0.1.0")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(api_router)
    application.include_router(cards.router)
    return application


app = create_app()
