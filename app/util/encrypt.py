import hashlib
import base64
from Crypto.Cipher import AES

BS: int = 16
pad = (lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS).encode())
unpad = (lambda s: s[:-ord(s[len(s) - 1:])])


class AESCipher(object):
    def __init__(self, key):
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, msg):
        try:
            msg = msg.encode('utf-8')
            raw = pad(msg)
            cipher = AES.new(self.key, AES.MODE_CBC, self.__iv.encode('utf-8'))
            enc = cipher.encrypt(raw)
            return base64.b64encode(enc).decode('utf-8')
        except Exception as e:
            print(str(e))
            raise e

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        cipher = AES.new(self.key, AES.MODE_CBC, self.__iv.encode('utf-8'))
        dec = cipher.decrypt(enc)
        return unpad(dec).decode('utf-8')

    @property
    def __iv(self):
        return chr(10) * BS
