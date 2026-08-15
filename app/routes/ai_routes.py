import os
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.auth import get_current_user
from app.ai_agent import ai_agent
from app.config import WORKSPACES_DIR

router = APIRouter(prefix="/api/ai", tags=["AI Agent"])

class AIAssistRequest(BaseModel):
    project_id: str
    filename: Optional[str] = "main.tex"
    code: Optional[str] = None
    user_prompt: Optional[str] = None
    errors: Optional[List[Dict[str, Any]]] = []
    warnings: Optional[List[Dict[str, Any]]] = []
    api_key: Optional[str] = None
    provider: Optional[str] = "auto"

@router.post("/assist")
async def ai_assist(payload: AIAssistRequest, current_user: dict = Depends(get_current_user)):
    """
    AI Agent endpoint to diagnose, explain, and generate corrected LaTeX code.
    """
    user_id = current_user["id"]
    project_dir = WORKSPACES_DIR / str(user_id) / payload.project_id
    
    code = payload.code
    if not code:
        file_path = project_dir / payload.filename
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                code = f.read()
        else:
            raise HTTPException(status_code=404, detail="File not found")

    try:
        result = ai_agent.generate_fix(
            latex_code=code,
            errors=payload.errors or [],
            warnings=payload.warnings or [],
            user_prompt=payload.user_prompt,
            api_key=payload.api_key,
            provider=payload.provider or "auto"
        )
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
