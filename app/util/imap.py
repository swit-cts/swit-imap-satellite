import os
import email
import imaplib
from enum import Enum
from email import policy
from email.header import decode_header
from app.const import const
from app.schemas import schema_email


class ImapSearchOption(Enum):
    ALL = "(ALL)"
    UNSEEN = "(UNSEEN)"


class ImapUtil:
    def __init__(self):
        super().__init__()
        self.session = None

    def connect(
            self,
            user_id: str,
            password: str
    ):
        try:
            self.session = imaplib.IMAP4_SSL(const.EMAIL_HOST)
            self.session.login(user_id, password)
        except Exception as e:
            raise e

    def search(self, mailbox: str, option: ImapSearchOption):
        # 편지함 이름 선택
        self.session.select(mailbox)
        # 편지함 검색
        result, data = self.session.search(None, option.value)
        return result, data

    def get_box_list(self):
        ret_list = []
        result, box_list = self.session.list()
        if result == "OK":
            for idx, box in enumerate(box_list):
                str_box = box.decode("utf-8").split(' "/" ')
                str_box = str_box[1].replace('"', '')
                ret_list.append(str_box)
            return ret_list
        else:
            return None

    def get_message(self, user_id: str, uid: int) ->  schema_email.Email:
        try:
            # 메일 정보 읽기
            result, data = self.session.fetch(uid, "(RFC822)")

            if result == "OK":
                # 메일 기본정보 출력
                raw_email = data[0][1]
                raw_email_string = raw_email.decode("UTF-8", "ignore")
                email_message = email.message_from_string(s=raw_email_string, policy=policy.default)
                subject, encode = __find_encoding_info__(email_message['Subject'])

                mail = schema_email.Email()
                mail.user_id = user_id
                mail.eml_subject = subject
                mail.eml_from = email_message['From']
                mail.eml_to = email_message['To']
                mail.eml_sender = email_message['Sender']
                mail.received_at = email_message['Date']

                message = ''

                if email_message.is_multipart():
                    for part in email_message.get_payload():
                            if str(part.get_content_type()).startswith("html"):
                                # 멀티파트 일때 부분적으로 메시지를 가져 온다.
                                message_part = part.get_payload(decode=True)
                                # 디코딩을 했는데 정보가 없다면 디코드를 하지 않고 가져 온다.
                                if message_part is None:
                                    message_part = part.get_payload(decode=False)
                                    # 이때는 배열형으로 가져 오기 때문에 아이템을 나눠서 넣어준다.
                                    for p in message_part:
                                        message += str(p)
                                else:
                                    message += message_part
                else:
                    bytes = email_message.get_payload(decode=True)
                    encode = email_message.get_content_charset()
                    message = bytes.decode(encode, "ignore")

                mail.eml_content = message

                attach_list = []

                # 첨부파일 읽기
                for part in email_message.walk():
                    attach = schema_email.EmailAttachment()
                    if part.get_content_maintype() == "multipart":
                        continue
                    if part.get("Content-Disposition") is None:
                        continue
                    file_name = part.get_filename()

                    if bool(file_name):
                        os.makedirs(const.STORAGE_PATH, exist_ok=True)
                        file_path = os.path.join(const.STORAGE_PATH, file_name)
                        attach.file_path = file_path
                        attach.file_name = file_name
                        attach.file_size = len(part.get_payload(decode=True))
                        attach.content_type = part.get_content_type()

                        if not os.path.isfile(file_path):
                            fp = open(file_path, "wb")
                            fp.write(part.get_payload(decode=True))
                            fp.close()
                            attach_list.append(attach)
                    else:
                        continue
                mail.attaches = attach_list
                return mail
            else:
                raise Exception("메일 읽기 실패")
        except Exception as e:
            raise e

    def close(self):
        self.session.close()
        self.session.logout()

def __find_encoding_info__(txt: str):
    info = email.header.decode_header(txt)
    s, encoding = info[0]
    return s, encoding
