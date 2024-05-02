import uuid
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from datetime import datetime, timedelta

from app.database import Base


class UserInfo(Base):
    """
    사용자 정보
    """
    __tablename__ = "com_user_info"
    user_id: str | Column = Column(String(36), name="user_id", nullable=False, unique=True, primary_key=True, default=str(uuid.uuid4()))
    email: str | Column = Column(String(100), name="email", nullable=False)
    password: str | Column = Column(String(255), name="password", nullable=False)
    created_at: datetime | Column = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow() + timedelta(hours=9))
    role: str | Column = Column(String(10), name="role", nullable=False, default="MEMBER")
    is_active: bool | Column = Column(Boolean, name="is_active", nullable=False, default=True)
    access_token: str | Column = Column(String(255), name="access_token", nullable=True)
    refresh_token: str | Column = Column(String(255), name="refresh_token", nullable=True)


class UserEmailAuth(Base):
    """
    사용자 이메일 접속 정보
    """
    __tablename__ = "com_user_email_auth"
    user_id: str | Column = Column(String(36), ForeignKey("com_user_info.user_id"), nullable=False, primary_key=True)
    email: str | Column = Column(String(100), name="email", nullable=False)
    password: str | Column = Column(String(255), name="password", nullable=False)
    created_at: datetime | Column = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow())
    updated_at: datetime | Column = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow())