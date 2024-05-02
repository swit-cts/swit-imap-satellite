from fastapi import APIRouter, Query
from fastapi.security import OAuth2PasswordBearer
from starlette.responses import JSONResponse

from app.schemas import schema_email
from app.services import service_picker, service_mail
from app.util.imap import ImapUtil, ImapSearchOption


router = APIRouter(
    prefix="/eml",
    tags=["Email"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/signin")


@router.get(
    path="/test",
    description="Email 수집 테스트",
)
async def get_eml_test(
        id: str,
        pw: str
):
    try:
        imap = ImapUtil()
        # 아이맵에 로그인
        imap.connect(user_id=id, password=pw)
        # 읽지 않은 메일을 가져온다.
        result, [msg_ids] = imap.search(mailbox="Inbox", option=ImapSearchOption.UNSEEN)

        if result == "OK":
            for uid in msg_ids.split():
                imap.get_message(box="INBOX", user_id=id, uid=uid)

        imap.close()
        return result
    except Exception as e:
        print(e)

@router.get(
    path="/service.test",
)
async def mail_picker_test():
    saved_count = await service_picker.email_picker()
    return saved_count



@router.get(
    path="/email.list",
    response_class=JSONResponse,
    response_model=list[schema_email.Email]
)
async def get_emails(user_id: str = Query(title="user_id", description="사용자 아이디", example="1ec3294b-ed69-4339-88b4-c09985398ac2")):
    ret_list = await service_mail.get_emails(user_id=user_id)
    return ret_list


@router.get(
    path="/email/{eml_id}"
)
async def get_email(eml_id: str):
    ret_mail = await service_mail.get_email(eml_id=eml_id)
    return ret_mail