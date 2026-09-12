from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.api.dependencies import require_admin
from app.models.database import SessionLocal
from app.models.user import User
from app.utils.security import hash_password


router = APIRouter(
    prefix="/users",
    tags=["User Management"]
)


# =========================
# Database Dependency
# =========================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================
# Request / Response Models
# =========================

class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str


class CreateUserResponse(BaseModel):
    message: str
    user_id: int
    name: str
    email: str
    role: str


# =========================
# Get All Users
# =========================

@router.get("/")
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    users = (
        db.query(User)
        .order_by(User.created_at.desc())
        .all()
    )

    return {
        "total_users": len(users),
        "users": [
            {
                "user_id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at
            }
            for user in users
        ]
    }


# =========================
# Create Admin / Employee
# =========================

@router.post(
    "/",
    response_model=CreateUserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(
    user_data: CreateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    name = user_data.name.strip()
    email = user_data.email.strip().lower()
    role = user_data.role.strip().lower()
    password = user_data.password

    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name cannot be empty."
        )

    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long."
        )

    if role not in {"admin", "employee"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be either admin or employee."
        )

    existing_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered."
        )

    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role=role,
        is_active=True
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return CreateUserResponse(
        message="User created successfully.",
        user_id=user.id,
        name=user.name,
        email=user.email,
        role=user.role
    )