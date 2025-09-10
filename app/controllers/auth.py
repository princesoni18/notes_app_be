from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from app.models.users import TokenData, UserCreate, UserInDB, UserResponse
from app.utils.database import get_db
import os
from dotenv import load_dotenv

load_dotenv()

# Security configurations
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 12000

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class AuthController:
    def __init__(self):
        self.pwd_context = pwd_context

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Generate password hash"""
        return self.pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email"""
        db = await get_db()
        user = await db.users.find_one({"email": email})
        if user:
            return UserInDB(**user)
        return None

    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        """Authenticate user credentials"""
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    async def create_user(self, user: UserCreate):
        """Create new user and return user info with access token"""
        db = await get_db()
        # Check if user already exists
        if await db.users.find_one({"email": user.email}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        # Create user document
        user_dict = {
            "email": user.email,
            "full_name": user.full_name,
            "hashed_password": self.get_password_hash(user.password),
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        result = await db.users.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id
        user_response = UserResponse(**user_dict)
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        return {
            "user": user_response,
            "access_token": access_token,
            "token_type": "bearer"
        }

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> UserResponse:
        """Get current authenticated user"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
            token_data = TokenData(email=email)
        except JWTError:
            raise credentials_exception
        
        user = await self.get_user_by_email(email=token_data.email)
        if user is None:
            raise credentials_exception
        
        return UserResponse(**user.dict())

auth_controller = AuthController()      