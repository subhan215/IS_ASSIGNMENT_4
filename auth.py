# auth.py
import hashlib
from db import get_user_by_username, add_log, get_conn as _get_conn

SALT = "static_salt_for_demo"  # For assignment; note in report to use per-user salt & bcrypt/argon2 in prod

def hash_password(password: str) -> str:
    return hashlib.sha256((SALT + password).encode()).hexdigest()

def verify_password(password: str, stored_hash: str) -> bool:
    return hash_password(password) == stored_hash

def login(username: str, password: str):
    """
    Return (user_dict, None) if success, otherwise (None, error_message)
    user_dict contains user_id, username, role, password_hash (we'll keep it but UI should not show)
    """
    try:
        user = get_user_by_username(username)
    except Exception as e:
        return None, f"DB error: {e}"

    if not user:
        # don't call add_log because user not found (no user_id). Optionally log a generic failed attempt.
        return None, "User not found"

    stored = user.get("password_hash", "")
    # If stored seems empty, fail safely
    if not stored:
        add_log(user['user_id'], user['username'], user['role'], "login", "failed - no password hash")
        return None, "Invalid credentials"

    if verify_password(password, stored):
        add_log(user['user_id'], user['username'], user['role'], "login", "successful")
        # Remove password_hash from returned dict for safety (but keep user_id/username/role)
        return {"user_id": user["user_id"], "username": user["username"], "role": user["role"]}, None
    else:
        add_log(user['user_id'], user['username'], user['role'], "login", "failed - wrong password")
        return None, "Invalid credentials"
