from pydantic import BaseModel, Field


class UserAuth(BaseModel):
    email: str | None = Field(title="email", description="Email address", example="johnny.kim@swit.io", default=None)
    password: str | None = Field(title="password", description="Password", default=None)

    class Config:
        from_attributes = True
