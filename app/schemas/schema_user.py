from datetime import datetime
from pydantic import BaseModel, Field


class UserAuth(BaseModel):
    email: str | None = Field(title="email", description="Email address", example="johnny.kim@swit.io", default=None)
    password: str | None = Field(title="password", description="Password", default=None)

    class Config:
        from_attributes = True


class UserInfo(UserAuth):
    user_id: str  | None = Field(title="user_id", description="사용자 아이디", default=None)
    created_at: datetime | None = Field(title="created_at", description="생성일시", default=None)
    role: str | None = Field(title="role", description="사용자 권한", default=None)
    is_active: bool | None = Field(title="is_active", description="사용중 여부", default=None)
    access_token: str | None = Field(title="access_token", description="접근용 토큰", default=None)
    refresh_token: str | None = Field(title="refresh_token", description="갱신용 토큰", default=None)

    class Config:
        from_attributes = True