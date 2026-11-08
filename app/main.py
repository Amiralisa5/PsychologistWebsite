import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.seed_data import seed_database
from app.routes.public import router as public_router
from app.routes.api import router as api_router
from app.routes.admin import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure database tables & seed data exist
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield
    # Shutdown logic if needed


app = FastAPI(
    title="Psychologist & Therapist Web Application",
    description="Bilingual (English & Persian) website with client booking and therapist management portal.",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Include Routers
app.include_router(public_router)
app.include_router(api_router)
app.include_router(admin_router)
