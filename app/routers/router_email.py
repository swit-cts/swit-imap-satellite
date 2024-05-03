import logging
from typing import Annotated
from fastapi import APIRouter, Path, Depends, status, Query
from fastapi.security import OAuth2PasswordBearer
from fastapi.exceptions import HTTPException
from starlette.responses import JSONResponse

from app.schemas import schema_email, schema_user
from app.services import service_mail
from app.util import security

logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin")

router = APIRouter(prefix="/eml", tags=["Email"])


@router.get(
    path="/email.sync",
    summary="IMAP과 동기화",
    response_class=JSONResponse
)
async def get_email_sync(
        current_user: Annotated[schema_user.UserInfo, Depends(security.get_current_user)]
):
    """
    > IMAP 서버와 메일을 동기화 한다.

    * :param current_user: 로그인한 사용자
    * :return:
    """
    try:
        # 이메일 동기화를 한다.
        save_count = await service_mail.get_sync_imap(current_user.user_id)
        ret_list = await service_mail.get_emails(user_id=current_user.user_id)
        return {"received": save_count, "data": ret_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    path="/email.list",
    response_class=JSONResponse,
    response_model=list[schema_email.EmailListResponse]
)
async def get_emails(
        current_user: Annotated[schema_user.UserInfo, Depends(security.get_current_user)],
        keyword: str | None = Query(title="keyword", description="검색어", default=None),
        search_option: str | None= Query(title="search_option", description="검색 옵션", default=None),
        order_column: str | None= Query(title="order_column", description="정렬 기준 컬럼", default=None),
        order_direction: str | None= Query(title="order_direction", description="정렬 방향", default=None),
):
    """
    이메일 목록을 가져 온다.
    :param current_user: 로그인한 사용자
    :return:
    """
    try:
        ret_list = await service_mail.get_emails(
            user_id=current_user.user_id,
            keyword=keyword,
            search_option=search_option,
            order_column=order_column,
            order_direction=order_direction
        )
        return ret_list
    except Exception as e:
        raise e


@router.get(
    path="/email/{eml_id}"
)
async def get_email(
        eml_id: str = Path(title="eml_id", description="이메일 아이디"),
        current_user: schema_user.UserInfo = Depends(security.get_current_user)
):
    """
    선택한 이메일의 내용을 가져온다.
    :param current_user: 로그인한 사용자
    :param eml_id: 이메일 아이디
    :return:
    """
    try:
        ret_mail = await service_mail.get_email(eml_id=eml_id)
        if current_user.user_id != ret_mail.user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="잘못된 접근 입니다.")
        return ret_mail
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))