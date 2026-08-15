import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routes.auth_routes import router as auth_router
from app.routes.project_routes import router as project_router
from app.routes.file_routes import router as file_router
from app.routes.compile_routes import router as compile_router
from app.routes.view_routes import router as view_router
from app.routes.ai_routes import router as ai_router

STATIC_DIR = Path(__file__).resolve().parent / "static"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database on startup
    init_db()
    yield

app = FastAPI(
    title="Overleaf LaTeX Engine",
    description="Profound, real-time LaTeX to PDF editor with auto-suggestions",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
os.makedirs(STATIC_DIR / "css", exist_ok=True)
os.makedirs(STATIC_DIR / "js", exist_ok=True)
os.makedirs(STATIC_DIR / "assets", exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Include routers
app.include_router(auth_router)
app.include_router(project_router)
app.include_router(file_router)
app.include_router(compile_router)
app.include_router(view_router)
app.include_router(ai_router)

# Custom exception handler for 401 redirecting browser HTML requests to /login
@app.exception_handler(status.HTTP_401_UNAUTHORIZED)
async def unauthorized_handler(request: Request, exc):
    accept_header = request.headers.get("accept", "")
    if "text/html" in accept_header and not request.url.path.startswith("/api/"):
        return RedirectResponse(url=f"/login?next={request.url.path}", status_code=status.HTTP_302_FOUND)
    return JSONResponse(status_code=401, content={"detail": exc.detail or "Unauthorized"})
