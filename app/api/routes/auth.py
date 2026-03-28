from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import create_access_token, get_current_user, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import TokenResponseSchema, UserLoginSchema, UserReadSchema, UserRegisterSchema

router = APIRouter(prefix="/auth", tags=["auth"])


def _to_user_schema(user: User) -> UserReadSchema:
    return UserReadSchema(
        id=user.id,
        username=user.username,
        created_at=user.created_at.isoformat(),
    )


@router.post("/register", response_model=TokenResponseSchema, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegisterSchema, db: Session = Depends(get_db)) -> TokenResponseSchema:
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名已存在")

    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponseSchema(access_token=create_access_token(user.username), user=_to_user_schema(user))


@router.post("/login", response_model=TokenResponseSchema)
def login(payload: UserLoginSchema, db: Session = Depends(get_db)) -> TokenResponseSchema:
    user = db.query(User).filter(User.username == payload.username).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账号或密码错误")
    return TokenResponseSchema(access_token=create_access_token(user.username), user=_to_user_schema(user))


@router.get("/me", response_model=UserReadSchema)
def me(current_user: User = Depends(get_current_user)) -> UserReadSchema:
    return _to_user_schema(current_user)
