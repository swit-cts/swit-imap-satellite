from uuid import uuid4
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi_sqlalchemy import db
from sqlalchemy.exc import SQLAlchemyError

from app.schemas import schema_email
from app.models.model_email import Email, EmailAttachment


def is_exists(user_id:str, eml_uid: int) -> bool:
    # 이미 수집한 이메일인지 체크
    try:
        email = db.session.query(Email).filter(Email.user_id == user_id, Email.eml_uid == eml_uid).one()
        return email is not None
    except:
        return False


def save_emails(mails: list[schema_email.Email]) -> int:
    saved_count = 0
    with db.session as session:
        try:
            for mail in mails:
                if not is_exists(mail.user_id, mail.eml_uid):
                    eml_id = str(uuid4())
                    email = Email(
                        eml_id=eml_id,
                        eml_uid=mail.eml_uid,
                        user_id=mail.user_id,
                        eml_from=mail.eml_from,
                        eml_sender=mail.eml_sender,
                        eml_to=mail.eml_to,
                        eml_subject=mail.eml_subject,
                        eml_content=mail.eml_content,
                        received_at=mail.received_at
                    )
                    # 메일 정보를 먼저 저장한다.
                    session.add(email)
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


async def get_emails(user_id: str) -> list[schema_email.Email]:
    try:
        # 먼저 이메일 정보를 가져온다.
       ret_list: list[schema_email.Email] = db.session.query(Email).filter(Email.user_id == user_id).all()
       return ret_list
    except SQLAlchemyError as exc:
        raise exc


async def get_email(eml_id: str) -> schema_email.Email:
    try:
        ret_obj: schema_email.Email = db.session.query(Email).filter(Email.eml_id == eml_id).one()
        attach_list = db.session.query(EmailAttachment).filter(EmailAttachment.eml_id == eml_id).all()
        ret_obj.attaches = attach_list
        return ret_obj
    except SQLAlchemyError as exc:
        raise exc
