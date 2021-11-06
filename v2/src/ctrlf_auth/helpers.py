import random
import string
from typing import Dict

from ctrlf_auth.constants import SIGNING_TOKEN_MAX_AGE
from django.core import signing

ALL_LETTERS_AND_NUMBERS = string.ascii_letters + "".join(str(i) for i in range(10))
CODE_MAX_LENGTH = 8


def generate_auth_code():
    return "".join(random.choice(ALL_LETTERS_AND_NUMBERS) for _ in range(CODE_MAX_LENGTH))


def generate_signing_token(data: Dict):
    return signing.dumps(data, compress=True)


def decode_signing_token(token: str, max_age: int = SIGNING_TOKEN_MAX_AGE):
    try:
        payload = signing.loads(token, max_age=max_age)
    except signing.SignatureExpired:
        raise ValueError("token이 만료되었습니다.")
    except signing.BadSignature:
        raise ValueError("token이 유효하지 않습니다.")
    else:
        return payload
