from fastapi import APIRouter, HTTPException, status, Response, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.database import get_db_cursor
from app.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    full_name: Optional[str] = ""

class LoginRequest(BaseModel):
    username_or_email: str
    password: str

@router.post("/register")
def register(req: RegisterRequest, response: Response):
    with get_db_cursor() as cursor:
        # Check existing
        cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (req.username.strip(), req.email.lower().strip()))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or Email already registered"
            )

        hashed = hash_password(req.password)
        cursor.execute(
            "INSERT INTO users (username, email, hashed_password, full_name) VALUES (?, ?, ?, ?)",
            (req.username.strip(), req.email.lower().strip(), hashed, req.full_name or req.username)
        )
        user_id = cursor.lastrowid

    # Create token
    access_token = create_access_token(data={"sub": req.username.strip(), "uid": user_id})
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=60 * 60 * 24 * 7,
        samesite="lax"
    )

    return {
        "success": True,
        "message": "User registered successfully",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "username": req.username.strip(),
            "email": req.email.lower().strip(),
            "full_name": req.full_name or req.username
        }
    }

@router.post("/login")
def login(req: LoginRequest, response: Response):
    identifier = req.username_or_email.strip()
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (identifier, identifier.lower()))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username/email or password"
            )

        user_dict = dict(user)
        if not verify_password(req.password, user_dict["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username/email or password"
            )

    access_token = create_access_token(data={"sub": user_dict["username"], "uid": user_dict["id"]})
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=60 * 60 * 24 * 7,
        samesite="lax"
    )

    return {
        "success": True,
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user_dict["id"],
            "username": user_dict["username"],
            "email": user_dict["email"],
            "full_name": user_dict.get("full_name") or user_dict["username"],
            "avatar_url": user_dict.get("avatar_url")
        }
    }

@router.get("/me")
def get_profile(current_user: dict = Depends(get_current_user)):
    return {
        "success": True,
        "user": current_user
    }

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"success": True, "message": "Logged out successfully"}
