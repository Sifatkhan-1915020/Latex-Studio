import os
import aiofiles
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from pydantic import BaseModel
from app.database import get_db_cursor
from app.auth import get_current_user
from app.config import WORKSPACES_DIR

router = APIRouter(prefix="/api/projects/{project_id}/files", tags=["files"])

class SaveFileRequest(BaseModel):
    filename: str
    content: str

class CreateFileRequest(BaseModel):
    filename: str
    content: Optional[str] = ""

@router.get("")
def list_files(project_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db_cursor() as cursor:
        cursor.execute("SELECT id FROM projects WHERE id = ? AND user_id = ?", (project_id, user_id))
        if not cursor.fetchone():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        cursor.execute("SELECT * FROM project_files WHERE project_id = ? ORDER BY is_main DESC, filename ASC", (project_id,))
        files = [dict(f) for f in cursor.fetchall()]

    return {"success": True, "files": files}

@router.get("/{filename:path}")
def get_file_content(project_id: str, filename: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM projects WHERE id = ? AND user_id = ?", (project_id, user_id))
        if not cursor.fetchone():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    file_path = WORKSPACES_DIR / str(user_id) / project_id / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File '{filename}' not found")

    # Check if binary (e.g. image)
    ext = file_path.suffix.lower()
    is_binary = ext in [".png", ".jpg", ".jpeg", ".gif", ".pdf", ".svg", ".ico", ".webp"]

    if is_binary:
        return {
            "success": True,
            "filename": filename,
            "is_binary": True,
            "content": f"/api/projects/{project_id}/files/{filename}/raw"
        }

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        return {
            "success": True,
            "filename": filename,
            "is_binary": False,
            "content": content
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error reading file: {str(e)}")

@router.post("")
def save_or_create_file(project_id: str, req: SaveFileRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    filename = req.filename.strip()
    if not filename or ".." in filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename")

    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM projects WHERE id = ? AND user_id = ?", (project_id, user_id))
        proj = cursor.fetchone()
        if not proj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    file_path = WORKSPACES_DIR / str(user_id) / project_id / filename
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(req.content)

    size_b = len(req.content.encode("utf-8"))
    ext = Path(filename).suffix.lower()
    file_type = "tex" if ext == ".tex" else ("bib" if ext == ".bib" else ("sty" if ext == ".sty" else "txt"))
    is_main = 1 if filename == proj["main_file"] else 0

    with get_db_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO project_files (project_id, filename, file_type, is_main, size_bytes, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(project_id, filename) DO UPDATE SET
                size_bytes = excluded.size_bytes,
                updated_at = CURRENT_TIMESTAMP
            """,
            (project_id, filename, file_type, is_main, size_b)
        )
        cursor.execute("UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (project_id,))

    return {
        "success": True,
        "message": "File saved",
        "file": {
            "filename": filename,
            "size_bytes": size_b,
            "file_type": file_type,
            "is_main": is_main
        }
    }

@router.delete("/{filename:path}")
def delete_file(project_id: str, filename: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db_cursor() as cursor:
        cursor.execute("SELECT main_file FROM projects WHERE id = ? AND user_id = ?", (project_id, user_id))
        proj = cursor.fetchone()
        if not proj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        if filename == proj["main_file"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete main LaTeX file")

        cursor.execute("DELETE FROM project_files WHERE project_id = ? AND filename = ?", (project_id, filename))
        cursor.execute("UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (project_id,))

    file_path = WORKSPACES_DIR / str(user_id) / project_id / filename
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception:
            pass

    return {"success": True, "message": f"File '{filename}' deleted"}

@router.post("/upload")
async def upload_asset(
    project_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
    with get_db_cursor() as cursor:
        cursor.execute("SELECT id FROM projects WHERE id = ? AND user_id = ?", (project_id, user_id))
        if not cursor.fetchone():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    filename = Path(file.filename).name
    if not filename or ".." in filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename")

    dst_dir = WORKSPACES_DIR / str(user_id) / project_id
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst_path = dst_dir / filename

    content = await file.read()
    with open(dst_path, "wb") as f:
        f.write(content)

    size_b = len(content)
    ext = dst_path.suffix.lower()
    file_type = "image" if ext in [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"] else ("bib" if ext == ".bib" else "other")

    with get_db_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO project_files (project_id, filename, file_type, is_main, size_bytes, updated_at)
            VALUES (?, ?, ?, 0, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(project_id, filename) DO UPDATE SET
                size_bytes = excluded.size_bytes,
                updated_at = CURRENT_TIMESTAMP
            """,
            (project_id, filename, file_type, size_b)
        )
        cursor.execute("UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (project_id,))

    return {
        "success": True,
        "message": f"File '{filename}' uploaded successfully",
        "file": {
            "filename": filename,
            "size_bytes": size_b,
            "file_type": file_type
        }
    }
