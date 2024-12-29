from datetime import datetime, timedelta, UTC
from typing import Optional

from fastapi import Depends, HTTPException, status
import jsonpickle
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
import redis
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from src.database.db import get_db
from src.conf.config import settings
from src.services.users import UserService
from src.database.models import User, UserRole

class Hash:
    """
    Class to handle password hashing and verification.

    Methods:
    - verify_password(plain_password, hashed_password): Verify a plain password against a hashed password.
    - get_password_hash(password: str): Get the hashed version of a password.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        return self.pwd_context.hash(password)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def create_access_token(data: dict, expires_delta: Optional[int] = None):
    """
    Create an access token for authentication.

    Args:
    - data: Data to be encoded in the token.
    - expires_delta: Expiry duration for the token.

    Returns:
    - str: Encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """
    Get the current user based on the provided token.

    Args:
    - token: JWT token for authentication.
    - db: Database session.

    Returns:
    - User: Current user object.
    """
    r = redis.Redis(host='localhost', port=6379, db=0)

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload["sub"]
        if username is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception
    user_service = UserService(db)
    user = r.get(str(username))
    if user is None:
        user = await user_service.get_user_by_username(username)
        if user is None:
            raise credentials_exception
        r.set(str(user.username), jsonpickle.encode(user))
        r.expire(str(user.username), 3600)
        return user
    
    return jsonpickle.decode(user)

def create_email_token(data: dict):
    """
    Create a token for email verification.

    Args:
    - data: Data to be encoded in the token.

    Returns:
    - str: Encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    print(token)
    return token

async def get_email_from_token(token: str):
    """
    Get the email from the provided token.

    Args:
    - token: JWT token for email verification.

    Returns:
    - str: Email extracted from the token.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload["sub"]
        return email
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Неправильний токен для перевірки електронної пошти",
        )

def get_current_admin_user(current_user: User = Depends(get_current_user)):
    """
    Get the current user if they are an admin.

    Args:
    - current_user: Current user object.

    Returns:
    - User: Current admin user.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Недостатньо прав доступу")
    return current_user
