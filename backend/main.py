from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes.calculator import router

app = FastAPI(title="Main calculator")
app.include_router(router)
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
app.mount(
    "/",
    StaticFiles(directory=(frontend_dir), html=True),
    name="frontend"
)