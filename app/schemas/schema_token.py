from datetime import datetime, timedelta
from pydantic import BaseModel, Field


class TokenData(BaseModel):
    username: str | None = Field(title="username", description="authorization username", default=None)

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str | None = Field(title="access_token", description="인증용 토큰", max_length=255, default=None)
    refresh_token: str | None = Field(title="refresh_token", description="갱신용 토큰", max_length=100, default=None)
    expires_in: int | None = Field(title="expires_in", description="만료 시간", default=None)
    expires_at: datetime | None = Field(title="expires_at", description="만료 예정 일시", default=None)

    class Config:
        from_attributes = True
