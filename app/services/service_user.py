from typing import Optional
from uuid import uuid4
from sqlalchemy import Update
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.exc import NoResultFound, IntegrityError, SQLAlchemyError
from datetime import datetime, timedelta
from fastapi_sqlalchemy import db
from app.models import model_user
from app.util import security, encrypt


async def get_user_by_email(email: str) -> Optional[model_user.UserInfo]:
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
            new_user_id: str = str(uuid4())

            stmt = insert(model_user.UserInfo).values({
                "user_id": new_user_id,
                "email": email,
                "password": hashed_password,
                "created_at": create_at,
                "is_active": True,
                "role": "MEMBER"
            })

            stmt = stmt.on_duplicate_key_update(
                user_id=new_user_id,
                email=email
            )
            session.execute(stmt)
            session.flush()
            # 이메일 정보 저장
            stmt = insert(model_user.UserEmailAuth).values({
                "user_id": new_user_id,
                "email": email,
                "password": encrypt_password,
                "created_at": create_at,
                "updated_at": create_at
            })
            stmt.on_duplicate_key_update(
                user_id=new_user_id,
                email=email
            )
            session.execute(stmt)
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


def disable_users(user_ids):
    with db.session as session:
        for user_id in user_ids:
            try:
                # 사용자의 활성화 상태를 변경한다.
                session.query(model_user.UserInfo).filter_by(user_id=user_id).update({"is_active": False})
                session.commit()
            except SQLAlchemyError as e:
                session.rollback()


def get_user(user_id: str) -> Optional[model_user.UserInfo]:
    try:
        result = db.session.query(model_user.UserInfo).filter_by(user_id=user_id, is_active=True).one_or_none()
        return result
    except Exception as e:
        raise e
