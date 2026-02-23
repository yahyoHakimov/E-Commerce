from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.schemas import RegisterRequest, LoginRequest, TokenResponse
from app.modules.auth import service

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=TokenResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    return service.register_user(
        db=db,
        username=request.username,
        email=request.email,
        password=request.password,
    )

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    return service.login_user(
        db=db,
        username=request.username,
        password=request.password,
    )