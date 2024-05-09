from datetime import datetime
from pydantic import BaseModel, Field
from app.models.model_email import Email, EmailAttachment


class EmailAttachment(BaseModel):
    attach_id: str | None = Field(title="attach_id", description="첨부파일 아이디", default=None)
    eml_id: str | None = Field(title="eml_id", description="이메일 아이디", default=None)
    file_name: str | None = Field(title="file_name", description="파일명", default=None)
    file_path: str | None = Field(title="file_path", description="파일 저장경로", default=None)
    file_size: str | None = Field(title="file_size", description="파일 사이즈", default=None)
    content_type: str | None = Field(title="content_type", description="파일 유형", default=None)

    class Config:
        from_attribute = True


class Email(BaseModel):
    eml_id: str | None = Field(title="eml_id", description="이메일 아이디", max_length=36, default=None)
    user_id: str | None = Field(title="user_id", description="사용자 아이디", max_length=36, default=None)
    eml_uid: int | None = Field(title="uid", description="이메일 uid", default=None)
    box_nm: str | None = Field(title="box_nm", description="메일함", default=None)
    eml_from: str | None = Field(title="eml_from", description="보낸 사람", max_length=255, default=None)
    eml_sender: str | None = Field(title="eml_sender", description="sender", default=None)
    eml_to: str | None = Field(title="eml_to", max_length=255, description="받는 사람", default=None)
    eml_subject: str | None = Field(title="eml_subject", description="메일 제목", default=None)
    eml_content: str | None = Field(title="eml_content", description="메일 내용", default=None)
    received_at: str | None = Field(title="received_at", description="수신 일시", default=None)
    created_at: datetime | None = Field(title="created_at", description="등록 일시", default=None)
    attaches: list[EmailAttachment] | None = Field(title="attaches", description="첨부파일", default=None)
    is_read: bool | None = Field(title="is_read", description="읽음 여부", default=None)

    class Config:
        from_attribute = True


class EmailListResponse(BaseModel):
    eml_id: str | None = Field(title="eml_id", description="이메일 아이디", max_length=36, default=None)
    user_id: str | None = Field(title="user_id", description="사용자 아이디", max_length=36, default=None)
    eml_uid: int | None = Field(title="uid", description="이메일 uid", default=None)
    eml_from: str | None = Field(title="eml_from", description="보낸 사람", max_length=255, default=None)
    eml_sender: str | None = Field(title="eml_sender", description="sender", default=None)
    eml_to: str | None = Field(title="eml_to", max_length=255, description="받는 사람", default=None)
    eml_subject: str | None = Field(title="eml_subject", description="메일 제목", default=None)
    received_at: str | None = Field(title="received_at", description="수신 일시", default=None)
    is_read: bool | None = Field(title="is_read", description="is_read", default=None)
    attach_count: int | None = Field(title="attach_count", description="첨부 파일 수", default=None)

    class Config:
        from_attribute = True