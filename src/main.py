from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from langserve import add_routes

from src.agents import LLMResponseRunnableLambda, RelationshipIntelligenceRunnableLambda

frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"

app = FastAPI(
    title="Anarock One Relationship Intelligence API",
    version="1.0",
    description="API server exposing LLM and relationship intelligence runnables.",
    debug=True,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_model=None)
def index():
    if frontend_dist.exists():
        return FileResponse(frontend_dist / "index.html")
    return {"message": "Hello World"}


add_routes(app, LLMResponseRunnableLambda, path="/llm-response")
add_routes(app, RelationshipIntelligenceRunnableLambda, path="/relationship-intelligence")

if frontend_dist.exists():
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_frontend(full_path: str) -> FileResponse:
        requested_path = frontend_dist / full_path
        if requested_path.is_file():
            return FileResponse(requested_path)
        return FileResponse(frontend_dist / "index.html")
