import os
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query, Response
from fastapi.responses import FileResponse
from app.database import get_db_cursor
from app.auth import get_current_user
from app.compiler import compiler_service
from app.config import WORKSPACES_DIR

router = APIRouter(prefix="/api/projects/{project_id}", tags=["compile"])

@router.post("/compile")
def compile_project(project_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db_cursor() as cursor:
        cursor.execute("SELECT main_file FROM projects WHERE id = ? AND user_id = ?", (project_id, user_id))
        proj = cursor.fetchone()
        if not proj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        main_file = proj["main_file"] or "main.tex"

    # Run LaTeX compilation
    result = compiler_service.compile(user_id=user_id, project_id=project_id, main_file=main_file)

    pdf_url = None
    if result["success"]:
        # Add timestamp for cache busting in UI
        pdf_url = f"/api/projects/{project_id}/pdf?t={int(os.path.getmtime(result['pdf_path'])) if result.get('pdf_path') and os.path.exists(result['pdf_path']) else 0}"

    return {
        "success": result["success"],
        "duration_ms": result["duration_ms"],
        "errors": result["errors"],
        "warnings": result["warnings"],
        "healed": result.get("healed", False),
        "healed_content": result.get("healed_content", None),
        "fixes_applied": result.get("fixes_applied", []),
        "pdf_url": pdf_url,
        "raw_log": result["raw_log"]
    }

@router.get("/pdf")
def get_compiled_pdf(
    project_id: str,
    t: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
    with get_db_cursor() as cursor:
        cursor.execute("SELECT main_file FROM projects WHERE id = ? AND user_id = ?", (project_id, user_id))
        proj = cursor.fetchone()
        if not proj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        main_file = proj["main_file"] or "main.tex"

    pdf_name = Path(main_file).stem + ".pdf"
    pdf_path = WORKSPACES_DIR / str(user_id) / project_id / pdf_name

    if not pdf_path.exists() or pdf_path.stat().st_size == 0:
        # If PDF doesn't exist yet, compile it now!
        comp_res = compiler_service.compile(user_id=user_id, project_id=project_id, main_file=main_file)
        if not comp_res["success"] or not pdf_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF has not been compiled yet or compilation failed")

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Content-Disposition": f'inline; filename="{pdf_name}"'
        }
    )

@router.get("/download-pdf")
def download_pdf(project_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db_cursor() as cursor:
        cursor.execute("SELECT title, main_file FROM projects WHERE id = ? AND user_id = ?", (project_id, user_id))
        proj = cursor.fetchone()
        if not proj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        title = proj["title"]
        main_file = proj["main_file"] or "main.tex"

    pdf_name = Path(main_file).stem + ".pdf"
    pdf_path = WORKSPACES_DIR / str(user_id) / project_id / pdf_name

    if not pdf_path.exists():
        comp_res = compiler_service.compile(user_id=user_id, project_id=project_id, main_file=main_file)
        if not comp_res["success"] or not pdf_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF not compiled")

    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
    download_filename = f"{safe_title}.pdf"

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{download_filename}"'}
    )

@router.get("/logs")
def get_compilation_logs(project_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db_cursor() as cursor:
        cursor.execute("SELECT main_file FROM projects WHERE id = ? AND user_id = ?", (project_id, user_id))
        proj = cursor.fetchone()
        if not proj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        main_file = proj["main_file"] or "main.tex"

    log_name = Path(main_file).stem + ".log"
    log_path = WORKSPACES_DIR / str(user_id) / project_id / log_name

    content = ""
    if log_path.exists():
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

    return {"success": True, "logs": content}
