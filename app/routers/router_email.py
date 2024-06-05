import logging
from typing import Annotated
from fastapi import APIRouter, Path, Depends, status, Query
from fastapi.security import OAuth2PasswordBearer
from fastapi.exceptions import HTTPException
from starlette.responses import JSONResponse

from app.schemas import schema_user
from app.services import service_mail
from app.util import security

logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin")

router = APIRouter(prefix="/eml", tags=["Email"])


@router.get(path="/box.list")
async def get_box_list(
        current_user: Annotated[schema_user.UserInfo, Depends(security.get_current_user)]
):
    try:
        ret_list = []
        box_list = await service_mail.get_box_list(user_id=current_user.user_id)
        # INBOX, Sent Messages를 순서상 맨 앞으로 놓는다.
        ret_list.append({"box_id": "INBOX", "box_nm": "받은메일함"})
        ret_list.append({"box_id": "Sent Messages", "box_nm": "보낸메일함"})

        for box in box_list:
            if box.box_nm not in ["INBOX", "Sent Messages"]:
                ret_list.append({"box_id": box.box_nm, "box_nm": box.box_nm})

        return ret_list
    except Exception as e:
        raise HTTPException()

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
        save_count = await service_mail.get_sync_imap(current_user.user_id)
        ret_list = await service_mail.get_emails(user_id=current_user.user_id)
        return {"received": save_count, "data": ret_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    path="/email.list",
    response_class=JSONResponse
)
async def get_emails(
        current_user: Annotated[schema_user.UserInfo, Depends(security.get_current_user)],
        box_id: str | None = Query(title="box_id", description="메일함", default=None),
        keyword: str | None = Query(title="keyword", description="검색어", default=None),
        search_option: str | None= Query(title="search_option", description="검색 옵션", default=None),
        order_column: str | None= Query(title="order_column", description="정렬 기준 컬럼", default=None),
        order_direction: str | None= Query(title="order_direction", description="정렬 방향", default=None),
        page: int | None= Query(title="page", description="페이지 번호", default=0),
        page_size: int  | None= Query(title="page_size", description="한 페이지에 보여줄 레코드 수", default=15),
):
    """
    이메일 목록을 가져 온다.

    :param current_user: 로그인한 사용자
    :param box_id: 메일함
    :param keyword: 검색어
    :param search_option: 검색 옵션
    :param order_column: 정렬기준 컬럼
    :param order_direction: 정렬 방향
    :param page: 페이지 번호
    :param page_size: 한 페이지에 보여줄 레코드 수
    :return:
    """
    try:
        page_num = page * page_size
        total_count = await service_mail.get_total_count(
            user_id=current_user.user_id,
            box_id=box_id,
            keyword=keyword,
            search_option=search_option
        )
        ret_list = await service_mail.get_emails(
            user_id=current_user.user_id,
            box_id=box_id,
            keyword=keyword,
            search_option=search_option,
            order_column=order_column,
            order_direction=order_direction,
            offset=page_num,
            limit=page_size
        )
        return {"records": total_count, "data": ret_list}
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
        ret_mail = service_mail.get_email(eml_id=eml_id)
        print(ret_mail.eml_subject)
        if current_user.user_id != ret_mail.user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="잘못된 접근 입니다.")
        return ret_mail
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put(
    path="/email/read",
)
async def put_email_read(
        eml_id: str = Query(title="eml_id", description="읽음/안읽음 처리할 이메일의 아이디"),
        is_read: bool = Query(title="is_read", description="읽음/안읽음 여부")
):
    try:
        service_mail.update_read_email(eml_id=eml_id, is_read=is_read)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))