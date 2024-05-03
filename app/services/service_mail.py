from uuid import uuid4
from enum import Enum
from fastapi_sqlalchemy import db
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.util import encrypt
from app.util.imap import ImapUtil, ImapSearchOption
from app.schemas import schema_email
from app.models.model_email import Email, EmailAttachment
from app.models import model_user


class SearchOption(Enum):
    SUBJECT = "subject"
    CONTENT = "content"
    FROM = "from"

async def get_emails(
        user_id: str,
        keyword: str | None = None,
        search_option: str | None = None,
        order_column: str | None = None,
        order_direction: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
) -> list[schema_email.EmailListResponse]:
    """
    이메일 목록을 조회한다.
    :param user_id: 사용자 아이디
    :param keyword: 검색어
    :param search_option: 검색옵션
    :param order_column: 정렬 기준 컬럼
    :param order_direction: 정렬 방향
    :return:
    """
    mail_list: list[schema_email.EmailListResponse] = []

    if offset is None:
        offset = 0

    if limit is None:
        limit = 10

    if order_column is None:
        order_column = "received_at"
    if order_direction is None:
        order_direction = "desc"

    try:
        sql = f"""
            select
                 a.eml_id
                ,a.user_id
                ,a.eml_uid
                ,a.eml_subject
                ,a.eml_sender
                ,a.eml_from
                ,a.eml_to
                ,a.received_at
                ,a.is_read
                ,(SELECT COUNT(*) FROM eml_attachment_info eai WHERE eai.eml_id = a.eml_id) AS attach_count
            from
                eml_mail_info a
            where
                a.user_id = '{user_id}'
        """
        if search_option is not None:
            if search_option == "subject":
                sql += f" and a.eml_subject like '%{keyword}%'"
            elif search_option == "content":
                sql += f" and a.eml_content like '%{keyword}%'"
            elif search_option == "from":
                sql += f" and a.eml_from like '%{keyword}%'"
            else:
                pass
        sql += f" order by {order_column} {order_direction}"
        sql += f" limit {offset}, {limit}"

        print(sql)

        # 먼저 이메일 정보를 가져온다.
        ret_list: list[schema_email.EmailListResponse] = db.session.execute(text(sql)).all()
        # 쿼리에서 뽑을 경우 K,V 매핑이 되지 않으므로, 수동으로 할당 해 준다.
        mail_list = [
            schema_email.EmailListResponse(
                eml_id=i.eml_id,
                user_id=i.user_id,
                eml_uid=i.eml_uid,
                eml_subject=i.eml_subject,
                eml_sender=i.eml_sender,
                eml_from=i.eml_from,
                eml_to=i.eml_to,
                attach_count=i.attach_count,
                is_read=i.is_read,
                received_at=i.received_at) for i in ret_list
        ]

        return mail_list
    except SQLAlchemyError as exc:
        raise exc


async def get_email(eml_id: str) -> schema_email.Email:
    """
    이메일 상세 정보 조회
    :param eml_id: 이메일 아이디
    :return:
    """
    try:
        # 이메일 정보 조회
        ret_obj: schema_email.Email = db.session.query(Email).filter(Email.eml_id == eml_id).one()
        attach_list = db.session.query(EmailAttachment).filter(EmailAttachment.eml_id == eml_id).all()
        ret_obj.attaches = attach_list
        return ret_obj
    except SQLAlchemyError as exc:
        raise exc


def is_exists(user_id: str, eml_uid: int) -> bool:
    """
    Check if email is exists
    :param user_id: 사용자 아이디
    :param eml_uid: 이메일의 uid
    :return:
    """
    # 이미 수집한 이메일인지 체크
    try:
        email = db.session.query(Email).filter(Email.user_id == user_id, Email.eml_uid == eml_uid).one()
        return email is not None
    except Exception as e:
        print(str(e))
        return False


async def update_read_email(eml_id: str, is_read: bool) -> None:
    """
    읽음 처리
    :param eml_id: 이메일 아이디
    :param is_read: 읽음 여부
    :return:
    """
    try:
        email = db.session.query(Email).filter(Email.eml_id == eml_id).one()
        email.read = is_read
        db.session.add(email)
        db.session.commit()
    except SQLAlchemyError as exc:
        db.session.rollback()


def get_email_info(user_id: str):
    try:
        result = db.session.query(model_user.UserEmailAuth).filter_by(user_id=user_id).one_or_none()
        email_addr: str = result.email
        password: str = result.password
        return email_addr, password
    except Exception as e:
        raise e


async def get_sync_imap(user_id: str) -> int:
    """
    IMAP 서버와 정보 동기화
    :return:
    """
    try:
        saved_count = 0
        # 수집할 이메일의 목록
        mails: list[schema_email.Email] = []
        email, password = get_email_info(user_id=user_id)
        aes = encrypt.AESCipher(email)
        encrypted_password = aes.decrypt(password)
        imap = ImapUtil()
        # 서비스 접속
        imap.connect(user_id=email, password=encrypted_password)
        # 받은 메일함에서 읽지 않은 메일을 가져온다.
        result, [msg_ids] = imap.search(mailbox="INBOX", option=ImapSearchOption.UNSEEN)
        if result == "OK":
            if len(msg_ids.split()) > 0:
                for uid in msg_ids.split():
                    # UID를 이용해서 이메일을 읽어 온다.
                    email: schema_email.Email = imap.get_message(user_id=user_id, uid=uid)
                    email.eml_uid = int(uid)
                    # 수집 목록에 넣어준다.
                    mails.append(email)
                # 저장한다.
                saved_count = save_emails(mails=mails)
        else:
            raise Exception(result)
        imap.close()
        return saved_count
    except Exception as e:
        print(e)


def save_emails(mails: list[schema_email.Email]) -> int:
    saved_count = 0

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
                db.session.add(email)
                eml_id = email.eml_id
                for attach in mail.attaches:
                    attachment = EmailAttachment(
                        eml_id=eml_id,
                        file_name=attach.file_name,
                        file_size=attach.file_size,
                        content_type=attach.content_type,
                        file_path=attach.file_path
                    )
                    db.session.add(attachment)
                saved_count += 1
            db.session.commit()
        return saved_count
    except SQLAlchemyError as exc:
        db.session.rollback()
        raise exc