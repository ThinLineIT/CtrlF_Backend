import random
import string
from typing import Dict

from django.core import signing

ALL_LETTERS_AND_NUMBERS = string.ascii_letters + "".join(str(i) for i in range(10))
CODE_MAX_LENGTH = 8


def generate_auth_code():
    return "".join(random.choice(ALL_LETTERS_AND_NUMBERS) for _ in range(CODE_MAX_LENGTH))


def generate_signing_token(data: Dict):
    return signing.dumps(data, compress=True)
