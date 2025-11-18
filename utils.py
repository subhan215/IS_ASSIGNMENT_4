# utils.py
import hashlib
import re
from cryptography.fernet import Fernet
import os

# Try to load a Fernet key from file (optional; generate with create_key.py)
FERNET_KEY = None
if os.path.exists("fernet.key"):
    with open("fernet.key", "rb") as f:
        FERNET_KEY = f.read()

def generate_fernet_key():
    key = Fernet.generate_key()
    global FERNET_KEY
    FERNET_KEY = key
    return key

def encrypt_value(value: str) -> str:
    if not FERNET_KEY:
        raise ValueError("Fernet key not loaded")
    f = Fernet(FERNET_KEY)
    return f.encrypt(value.encode()).decode()

def decrypt_value(value: str) -> str:
    if not FERNET_KEY:
        raise ValueError("Fernet key not loaded")
    f = Fernet(FERNET_KEY)
    return f.decrypt(value.encode()).decode()
def mask_contact(contact: str) -> str:
    if not contact:
        return ""
    digits = re.sub(r'\D', '', contact)
    if len(digits) <= 4:
        return "XXX-XXX-" + digits
    return "XXX-XXX-" + digits[-4:]

def anonymize_name(name: str) -> str:
    if not name:
        return ""
    h = hashlib.sha256(name.encode()).hexdigest()
    return f"ANON_{h[:8]}"