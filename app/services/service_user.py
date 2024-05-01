from typing import Optional
from uuid import uuid4
from sqlalchemy import Update
from sqlalchemy.exc import NoResultFound, IntegrityError
from datetime import datetime, timedelta
from fastapi_sqlalchemy import db
from app.models import model_user
from app.util import security, encrypt


async def get_user(email: str) -> Optional[model_user.UserInfo]:
    with db.session as session:
        try:
            result = session.query(model_user.UserInfo).filter_by(email=email).one_or_none()
            return result
        except NoResultFound:
            return None


def create_user(email: str, password: str) -> None:
    """
    Creates new user with given email and password.
    :param email: 사용자 이메일
    :param password: 비밀번호
    :return:
    """
    with db.session as session:
        try:
            aes = encrypt.AESCipher(email)
            create_at: datetime = datetime.utcnow() + timedelta(hours=9)
            hashed_password = security.get_hashed_password(password)
            encrypt_password = aes.encrypt(password)
            new_user_id:str = str(uuid4())
            # 사용자 정보 저장
            new_user = model_user.UserInfo(
                user_id=new_user_id,
                email=email,
                password=hashed_password,
                created_at=create_at,
                is_active=True,
                role="MEMBER"
            )
            session.add(new_user)
            session.flush()
            # 이메일 정보 저장
            email_auth = model_user.UserEmailAuth(
                user_id=new_user_id,
                email=email,
                password=encrypt_password,
                created_at=create_at,
                updated_at=create_at
            )
            session.add(email_auth)
            session.commit()
        except IntegrityError as e:
            session.rollback()
            raise e


def get_active_users() -> Optional[list[model_user.UserInfo]]:
    with db.session as session:
        try:
            result = session.query(model_user.UserInfo).filter_by(is_active=True).all()
            return result
        except NoResultFound:
            return None


def get_all_users() -> Optional[list[model_user.UserInfo]]:
    """
    모든 사용자 가져오기 (관리자용)
    :return:
    """
    with db.session as session:
        result = session.query(model_user.UserInfo).all()
        return result


def get_email_info(user_id: str):
    try:
        result = db.session.query(model_user.UserEmailAuth).filter_by(user_id=user_id).one_or_none()
        email_addr: str = result.email
        password: str = result.password
        return email_addr, password
    except Exception as e:
        raise e


def disable_users(user_ids):
    with db.session as session:
        for user_id in user_ids:
            try:
                session.query(model_user.UserInfo).filter_by(user_id=user_id).update({"is_active": False})
                session.commit()
            except Exception as e:
                session.rollback()
