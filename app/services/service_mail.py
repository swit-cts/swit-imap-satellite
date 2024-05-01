from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi_sqlalchemy import db
from sqlalchemy.exc import SQLAlchemyError

from app.schemas import schema_email
from app.models.model_email import Email, EmailAttachment


def save_emails(mails: list[schema_email.Email]) -> int:
    saved_count = 0
    with db.session as session:
        try:
            for mail in mails:
                email = Email(
                    user_id=mail.user_id,
                    eml_box=mail.eml_box,
                    eml_from=mail.eml_from,
                    eml_sender=mail.eml_sender,
                    eml_to=mail.eml_to,
                    eml_subject=mail.eml_subject,
                    eml_content=mail.eml_content,
                    received_at=mail.received_at
                )
                # 메일 정보를 먼저 저장한다.
                session.add(email)
                session.flush()
                session.refresh(email)
                eml_id = email.eml_id
                for attach in mail.attaches:
                    attachment = EmailAttachment(
                        eml_id=eml_id,
                        file_name=attach.file_name,
                        file_size=attach.file_size,
                        content_type=attach.content_type,
                        file_path=attach.file_path
                    )
                    session.add(attachment)
                saved_count += 1
            session.commit()
            return saved_count
        except SQLAlchemyError as exc:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
