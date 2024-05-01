from fastapi import APIRouter
import email
import imaplib
from app.services import service_picker

from app.util.imap import ImapUtil, ImapSearchOption

router = APIRouter(
    prefix="/eml",
    tags=["Email"]
)


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