from app.util import encrypt
from app.util.imap import ImapUtil, ImapSearchOption
from app.schemas import schema_email
from app.services import service_user, service_mail
"""
Service Picker 이메일 수집 서비스

"""


async def email_picker():
    try:
        # 사용자 목록을 가져온다.
        users = service_user.get_active_users()
        saved_count = 0
        # 수집할 이메일의 목록
        mails: list[schema_email.Email] = []
        for user in users:
            email, password = service_user.get_email_info(user_id=user.user_id)
            aes = encrypt.AESCipher(email)
            encrypted_password = aes.decrypt(password)
            imap = ImapUtil()
            # 서비스 접속
            imap.connect(user_id=email, password=encrypted_password)
            # 메일 목록 가져오기
            box_list = imap.get_box_list()
            # 읽지 않은 메일을 가져온다.
            result, [msg_ids] = imap.search(mailbox="INBOX", option=ImapSearchOption.UNSEEN)
            if result == "OK":
                if len(msg_ids.split()) > 0:
                    for uid in msg_ids.split():
                        # UID를 이용해서 이메일을 읽어 온다.
                        email = imap.get_message(user_id=user.user_id, uid=uid)
                        email.eml_uid = int(uid)
                        # 수집 목록에 넣어준다.
                        mails.append(email)
                    # 저장한다.
                    saved_count = service_mail.save_emails(mails=mails)
            else:
                raise Exception(result)
            imap.close()
    except Exception as e:
        print(e)
    finally:
        return saved_count