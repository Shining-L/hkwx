import secrets
import string


def generate_key(length=32):
    # 由大小写字母、数字和标点符号组成的字符集
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for i in range(length))
