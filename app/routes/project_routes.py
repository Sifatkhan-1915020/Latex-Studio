import uuid
import shutil
import zipfile
import io
import os
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from app.database import get_db_cursor
from app.auth import get_current_user
from app.config import WORKSPACES_DIR
from app.templates_data import TEMPLATES

router = APIRouter(prefix="/api/projects", tags=["projects"])

class CreateProjectRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = ""
    template: Optional[str] = "blank"

class UpdateProjectRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    main_file: Optional[str] = None

@router.get("")
def list_projects(
    search: Optional[str] = Query(None),
    sort: Optional[str] = Query("updated_desc"),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
    with get_db_cursor() as cursor:
        query = "SELECT * FROM projects WHERE user_id = ? AND is_archived = 0"
        params = [user_id]

        if search and search.strip():
            query += " AND (title LIKE ? OR description LIKE ?)"
            s_param = f"%{search.strip()}%"
            params.extend([s_param, s_param])

        if sort == "title_asc":
            query += " ORDER BY title ASC"
        elif sort == "created_desc":
            query += " ORDER BY created_at DESC"
        else:
            query += " ORDER BY updated_at DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        projects = []
        for r in rows:
            p_dict = dict(r)
            # Count files in project
            cursor.execute("SELECT COUNT(*) as cnt FROM project_files WHERE project_id = ?", (p_dict["id"],))
            cnt_row = cursor.fetchone()
            p_dict["file_count"] = cnt_row["cnt"] if cnt_row else 0
            projects.append(p_dict)

    return {"success": True, "projects": projects}

@router.get("/templates")
def list_templates():
    tpl_list = []
    for k, v in TEMPLATES.items():
        tpl_list.append({
            "id": v["id"],
            "name": v["name"],
            "category": v["category"],
            "description": v["description"],
            "icon": v["icon"]
        })
    return {"success": True, "templates": tpl_list}

@router.post("")
def create_project(req: CreateProjectRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    project_id = str(uuid.uuid4())[:8]
    template_key = req.template if req.template in TEMPLATES else "blank"
    tpl_data = TEMPLATES[template_key]

    # Create workspace folder
    project_dir = WORKSPACES_DIR / str(user_id) / project_id
    os.makedirs(project_dir, exist_ok=True)

    with get_db_cursor() as cursor:
        cursor.execute(
            "INSERT INTO projects (id, user_id, title, description, template, main_file) VALUES (?, ?, ?, ?, ?, ?)",
            (project_id, user_id, req.title.strip(), req.description or "", template_key, "main.tex")
        )

        # Write template files
        for fname, fcontent in tpl_data["files"].items():
            fpath = project_dir / fname
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(fcontent)

            file_type = "tex" if fname.endswith(".tex") else ("bib" if fname.endswith(".bib") else "other")
            is_main = 1 if fname == "main.tex" else 0
            size_b = len(fcontent.encode("utf-8"))

            cursor.execute(
                "INSERT INTO project_files (project_id, filename, file_type, is_main, size_bytes) VALUES (?, ?, ?, ?, ?)",
                (project_id, fname, file_type, is_main, size_b)
            )

    return {
        "success": True,
        "message": "Project created successfully",
        "project": {
            "id": project_id,
            "title": req.title.strip(),
            "template": template_key,
            "main_file": "main.tex"
        }
    }

@router.get("/{project_id}")
def get_project(project_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM projects WHERE id = ? AND user_id = ?", (project_id, user_id))
        proj = cursor.fetchone()
        if not proj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        proj_dict = dict(proj)

        cursor.execute("SELECT * FROM project_files WHERE project_id = ? ORDER BY is_main DESC, filename ASC", (project_id,))
        files = [dict(f) for f in cursor.fetchall()]
        proj_dict["files"] = files

    return {"success": True, "project": proj_dict}

@router.put("/{project_id}")
def update_project(project_id: str, req: UpdateProjectRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM projects WHERE id = ? AND user_id = ?", (project_id, user_id))
        proj = cursor.fetchone()
        if not proj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        updates = []
        params = []
        if req.title is not None:
            updates.append("title = ?")
            params.append(req.title.strip())
        if req.description is not None:
            updates.append("description = ?")
            params.append(req.description.strip())
        if req.main_file is not None:
            updates.append("main_file = ?")
            params.append(req.main_file.strip())

        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.extend([project_id, user_id])
            cursor.execute(f"UPDATE projects SET {', '.join(updates)} WHERE id = ? AND user_id = ?", params)

    return {"success": True, "message": "Project updated"}

@router.post("/{project_id}/duplicate")
def duplicate_project(project_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM projects WHERE id = ? AND user_id = ?", (project_id, user_id))
        proj = cursor.fetchone()
        if not proj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        new_project_id = str(uuid.uuid4())[:8]
        new_title = f"{proj['title']} (Copy)"

        # Copy workspace directory
        src_dir = WORKSPACES_DIR / str(user_id) / project_id
        dst_dir = WORKSPACES_DIR / str(user_id) / new_project_id
        if src_dir.exists():
            shutil.copytree(src_dir, dst_dir)

        cursor.execute(
            "INSERT INTO projects (id, user_id, title, description, template, main_file) VALUES (?, ?, ?, ?, ?, ?)",
            (new_project_id, user_id, new_title, proj["description"], proj["template"], proj["main_file"])
        )

        cursor.execute("SELECT * FROM project_files WHERE project_id = ?", (project_id,))
        for f in cursor.fetchall():
            cursor.execute(
                "INSERT INTO project_files (project_id, filename, file_type, is_main, size_bytes) VALUES (?, ?, ?, ?, ?)",
                (new_project_id, f["filename"], f["file_type"], f["is_main"], f["size_bytes"])
            )

    return {"success": True, "project_id": new_project_id, "title": new_title}

@router.delete("/{project_id}")
def delete_project(project_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM projects WHERE id = ? AND user_id = ?", (project_id, user_id))
        proj = cursor.fetchone()
        if not proj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        cursor.execute("DELETE FROM project_files WHERE project_id = ?", (project_id,))
        cursor.execute("DELETE FROM projects WHERE id = ? AND user_id = ?", (project_id, user_id))

    # Delete workspace directory
    project_dir = WORKSPACES_DIR / str(user_id) / project_id
    if project_dir.exists():
        shutil.rmtree(project_dir, ignore_errors=True)

    return {"success": True, "message": "Project deleted"}

@router.get("/{project_id}/export-zip")
def export_project_zip(project_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM projects WHERE id = ? AND user_id = ?", (project_id, user_id))
        proj = cursor.fetchone()
        if not proj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    project_dir = WORKSPACES_DIR / str(user_id) / project_id
    if not project_dir.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace directory not found")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                file_path = Path(root) / file
                # Skip intermediate cache or lock files if any
                rel_path = file_path.relative_to(project_dir)
                zf.write(file_path, arcname=str(rel_path))

    zip_buffer.seek(0)
    safe_title = "".join(c for c in proj["title"] if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
    filename = f"{safe_title}_{project_id}.zip"

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
