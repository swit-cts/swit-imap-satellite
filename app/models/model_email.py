from sqlalchemy import Column, BigInteger, Integer, String , DateTime, Boolean
from sqlalchemy.dialects.mysql import LONGTEXT
from datetime import datetime, timedelta
from uuid import uuid4
from app.database import Base


class Email(Base):
    __tablename__ = 'eml_mail_info'
    # 메일 아이디
    eml_id: str | Column = Column(String(36), name="eml_id", nullable=False, primary_key=True, unique=True, default=str(uuid4()))
    # 메일 UID
    eml_uid: str | Column = Column(Integer, name="eml_uid", nullable=False, default=None)
    # 사용자 아이디
    user_id: str | Column = Column(String(36), name="user_id", nullable=False)
    # 보낸사람
    eml_from: str | Column = Column(String(255), name="eml_from", nullable=False, default=None)
    eml_sender: str | Column = Column(String(255), name="eml_sender", nullable=True, default=None)
    # 받는사람
    eml_to: str | Column = Column(String(255), name="eml_to", nullable=False, default=None)
    # 메일 제목
    eml_subject: str | Column = Column(String(255), name="eml_subject", nullable=False, default=None)
    # 메일 본문
    eml_content: str | Column = Column(LONGTEXT, name="eml_content", nullable=False, default=None)
    # 수신 일시
    received_at: str | Column = Column(String(50), name="received_at", nullable=False, default=None)
    # 등록일시
    created_at : DateTime | Column = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow() + timedelta(hours=9))
    # 읽음 여부
    is_read: bool | Column = Column(Boolean, nullable=True, default=False)

    def Email(
            self,
            eml_id: str,
            eml_uid: int,
            user_id: str,
            eml_from: str,
            eml_sender: str,
            eml_to: str,
            eml_subject: str,
            eml_content: str,
            received_at: str):
        self.eml_id = eml_id
        self.eml_uid = eml_uid
        self.user_id = user_id.strip()
        self.eml_from = eml_from.strip()
        self.eml_sender = eml_sender.strip()
        self.eml_to = eml_to.strip()
        self.eml_subject = eml_subject.strip()
        self.eml_content = eml_content.strip()
        self.received_at = received_at.strip()
        self.created_at = datetime.utcnow() + timedelta(hours=9)
        self.is_read = False
        return self


class EmailAttachment(Base):
    __tablename__ = 'eml_attachment_info'

    # 파일 아이디
    attach_id: str | Column = Column(String(36), name="attach_id", nullable=False, primary_key=True, default=str(uuid4()))
    eml_id: str | Column = Column(String(36), name="eml_id", nullable=False, primary_key=True,)
    file_name: str | Column = Column(String(255), name="file_name", nullable=False)
    file_path: str | Column = Column(String(255), name="file_path", nullable=False)
    file_size: int | Column = Column(BigInteger, name="file_size", nullable=False, default=0)
    content_type: str | Column = Column(String(255), name="content_type", nullable=True)

    def EmailAttachment(self, eml_id, file_name, file_path, file_size, content_type):
        self.eml_id = eml_id.strip()
        self.file_name = file_name.strip()
        self.file_path = file_path.strip()
        self.file_size = file_size
        self.content_type = content_type.strip()







