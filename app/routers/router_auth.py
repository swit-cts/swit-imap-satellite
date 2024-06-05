from typing import Annotated
from datetime import datetime, timedelta
from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import StarletteHTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas import schema_user, schema_token
from app.services import service_user
from app.util import security

router = APIRouter(
    prefix="/auth",
    tags=["사용자 인증"],
)

@router.post(
    path="/signup",
    summary="사용자 등록",
    response_class=JSONResponse,
)
async def post_auth_signup(param: schema_user.UserAuth):
    """
    사용자 등록
    :param param: 사용자 등록 정보
    :return:
    """
    try:
        # 현재 사용자가 가입되어 있는지 확인한다.
        user = await service_user.get_user(email=param.email)

        if user is not None:
            # 이미 존재하는 사용자일 경우
            raise StarletteHTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="exists")
        else:
            service_user.create_user(param.email, param.password)
            return {"result": "OK"}
    except Exception as e:
        raise StarletteHTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=(e))


@router.post(
    path="/signin",
    summary="사용자 로그인",
    response_model=schema_token.Token
)
async def post_auth_siginin(
        param: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    try:
        now = datetime.utcnow() + timedelta(hours=9)
        user = await security.authenticate_user(param.username, param.password)
        if not user:
            raise StarletteHTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="아이디나 비밀번호가 다릅니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token, expires_in = security.create_access_token(subject=user.user_id)
        refresh_token = security.create_refresh_token(subject=user.user_id)
        token = schema_token.Token()
        token.access_token = access_token
        token.refresh_token = refresh_token
        token.token_type = "Bearer"
        token.expires_in = expires_in
        token.expires_at = now + timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
        return token
    except Exception as e:
        raise e


