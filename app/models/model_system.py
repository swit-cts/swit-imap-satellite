from sqlalchemy import Column, String, DateTime
from datetime import datetime, timedelta
from app.database import Base


class Config(Base):
    """
    시스템 설정
    """
    __tablename__ = 'sys_config'
    key: str | Column = Column(String(30), name="key", nullable=False, unique=True, primary_key=True)
    value: str | Column = Column(String(255), name="value", nullable=False)
    created_at: datetime | Column = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow() + timedelta(hours=9))
    updated_at: datetime | Column = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow() + timedelta(hours=9))
