from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.users import UserLogin
from app.controllers.auth import auth_controller

from app.controllers.auth import ACCESS_TOKEN_EXPIRE_MINUTES
from app.models.users import Token, UserCreate, UserResponse, RegisterResponse, AuthResponse, UserMap

router = APIRouter()

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """Register a new user and return user info with access token"""
    result = await auth_controller.create_user(user)
    user_obj = result["user"]
    token = result["access_token"]
    user_map = UserMap(
        id=str(user_obj.id),
        email=user_obj.email,
        name=getattr(user_obj, "full_name", getattr(user_obj, "name", None)),
        token=token
    )
    return AuthResponse(user=user_map, access_token=token, token_type="bearer")

@router.post("/login", response_model=AuthResponse)
async def login(user: UserLogin):
    """Login user and return access token"""
    user_in_db = await auth_controller.authenticate_user(user.email, user.password)
    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_controller.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    user_map = UserMap(
        id=str(user_in_db.id),
        email=user_in_db.email,
        name=getattr(user_in_db, "full_name", getattr(user_in_db, "name", None)),
        token=access_token
    )
    return AuthResponse(user=user_map, access_token=access_token, token_type="bearer")

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(auth_controller.get_current_user)):
    """Get current user info"""
    return current_user