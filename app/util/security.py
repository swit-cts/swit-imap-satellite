from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from typing import Annotated
from datetime import datetime, timedelta

from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import Any
from passlib.context import CryptContext
from app.const import const
from app.schemas.schema_token import TokenData
from app.services import service_user

ACCESS_TOKEN_EXPIRE_MINUTES = 30    # 30분
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7일 (일주일)
ALGORITHM = 'HS256'
JWT_SECRET_KEY = const.JWT_SECRET_KEY
JWT_REFRESH_SECRET_KEY = const.JWT_REFRESH_SECRET_KEY

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin")


def get_hashed_password(password: str) -> str:
    """
    Returns a hashed password.
    :param password:  해싱할 비밀번호
    :return:
    """
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plaintext password and hashes it.
    :param plain_password: 검증할 비밀번호
    :param hashed_password: 대조할 비밀번호
    :return:
    """
    return password_context.verify(plain_password, hashed_password)


def create_access_token(subject: str | Any, expires_delta: int = None) -> str:
    """
    Access Token 생성
    :param subject:
    :param expires_delta:
    :return:
    """
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: str | Any, expires_delta: int = None) -> str:
    """
    Refresh Token 생성
    :param subject:
    :param expires_delta:
    :return:
    """
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token=token, key=JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as e:
        raise credentials_exception
    user = service_user.get_user(user_id=token_data.username)
    if user is None:
        raise credentials_exception
    return user
