import hashlib
from urllib import request
import rsa
import base64


class Comm(object):
    def __init__(self):
        super(Comm, self).__init__()

    @staticmethod
    def md5fun(data):
        m = hashlib.md5()
        b = str(data).encode(encoding='utf-8')
        m.update(b)
        str_md5 = m.hexdigest()
        return str_md5

    @staticmethod
    def rsa_decrypt(code):
        code = request.unquote(code)
        with open("wxmicrapp_private_pkcs1.pem", 'rb') as private_file:
            private_key = rsa.PrivateKey.load_pkcs1(private_file.read())
        code = base64.b64decode(code.encode('utf-8'))
        msg = rsa.decrypt(code, private_key).decode('utf-8')
        return msg