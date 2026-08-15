from pathlib import Path
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.auth import get_optional_current_user, get_current_user
from app.database import get_db_cursor
from app.templates_data import TEMPLATES

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter(include_in_schema=False)

@router.get("/", response_class=HTMLResponse)
def index_view(request: Request):
    user = get_optional_current_user(request)
    if user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

@router.get("/login", response_class=HTMLResponse)
def login_view(request: Request):
    user = get_optional_current_user(request)
    if user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"user": None}
    )

@router.get("/register", response_class=HTMLResponse)
def register_view(request: Request):
    user = get_optional_current_user(request)
    if user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"user": None}
    )

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_view(request: Request):
    user = get_optional_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "user": user,
            "templates": TEMPLATES
        }
    )

@router.get("/project/{project_id}", response_class=HTMLResponse)
def editor_view(project_id: str, request: Request):
    user = get_optional_current_user(request)
    if not user:
        return RedirectResponse(url=f"/login?next=/project/{project_id}", status_code=status.HTTP_302_FOUND)

    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM projects WHERE id = ? AND user_id = ?", (project_id, user["id"]))
        proj = cursor.fetchone()
        if not proj:
            return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
        proj_dict = dict(proj)

    return templates.TemplateResponse(
        request=request,
        name="editor.html",
        context={
            "user": user,
            "project": proj_dict
        }
    )
