import os

from uuid import uuid4
from imap_tools import MailBox, FolderInfo, MailMessage, MailMessageFlags, A
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
            self.session = MailBox(const.EMAIL_HOST).login(username=user_id, password=password)
            self.username = user_id
            self.password = password
        except Exception as e:
            raise e

    def search(self, option: ImapSearchOption):
        # 편지함 이름 선택
        self.session.select()
        # 편지함 검색
        result, data = self.session.search(None, option.value)
        return result, data

    def get_box_list(self):
        ret_list = []
        # imaplib에서 메일함 목록을 가져올 경우 한글에 문제가 있으므로, IMAP Utils를 사용한다.
        with self.session as mailbox:
            box_list: list[FolderInfo] = mailbox.folder.list()
            for box in box_list:
                if box.name not in ["Deleted Messages", "Junk"]:
                    ret_list.append(box.name)
            return ret_list

    def update_read(self, uid: list[str]):
        """
        메일 읽음 처리
        :param uids: 읽음 처리할 아이디
        :return:
        """
        try:
            with self.session as mailbox:
                mailbox.flag(uid_list=uid, flag_set=MailMessageFlags.SEEN, value=True)
        except Exception as e:
            raise e

    def logout(self):
        self.session.logout()

    def get_messages(self, user_id: str, box: str):
        try:
            email_list: list[schema_email.Email] = []
            with MailBox(const.EMAIL_HOST).login(username=self.username, password=self.password) as mailbox:
                mailbox.folder.set(folder=box)
                for msg in mailbox.fetch('(UNSEEN)', reverse=True):
                    mail = schema_email.Email()
                    mail.user_id = user_id
                    mail.box_nm = box
                    mail.eml_subject = msg.subject
                    mail.eml_from = msg.from_
                    mail.eml_sender = str(msg.cc).replace("(", '').replace(")", '').replace("'", "")
                    mail.eml_to = str(msg.to).replace("(", '').replace(")", '').replace("'", "")
                    mail.received_at = msg.date_str
                    mail.eml_content = msg.html
                    mail.eml_uid = msg.uid
                    mail.is_read = False

                    attach_list: list[schema_email.EmailAttachment] = []

                    for att in msg.attachments:
                        if att.filename is not None and len(att.filename) > 0:
                            attach = schema_email.EmailAttachment()
                            attach.attach_id = str(uuid4())
                            attach.content_type = att.content_type
                            attach.file_name = att.filename
                            os.makedirs(const.STORAGE_PATH, exist_ok=True)
                            file_path = os.path.join(const.STORAGE_PATH, attach.attach_id)
                            attach.file_path = file_path
                            attach.file_size = att.size
                            os.makedirs(const.STORAGE_PATH, exist_ok=True)

                            if not os.path.isfile(file_path):
                                fp = open(file_path, "wb")
                                fp.write(att.payload)
                                fp.close()
                                attach_list.append(attach)

                    mail.attaches = attach_list
                    email_list.append(mail)
            return email_list
        except Exception as e:
            raise e
