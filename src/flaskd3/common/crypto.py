import json
import logging
from cryptography.fernet import Fernet

global_key = "B4A98894-13B3-4406-B439-AE894C961CA6"


logger = logging.getLogger(__name__)


def encrypt_data(data, key=None):
    if not key:
        key = global_key
    json_str = json.dumps(data)
    cipher_processor = Fernet(key.encode())
    return cipher_processor.encrypt(json_str.encode()).decode()


def decrypt_data(data_str, key=None):
    if not key:
        key = global_key
    cipher_processor = Fernet(key.encode())
    data_json_str = cipher_processor.decrypt(data_str.encode()).decode()
    return json.loads(data_json_str)
