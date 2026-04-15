# File: c:/Users/work/Documents/lp-agent/backend/auth.py
# Purpose: Simple authentication utilities (password hashing and verification).

import hashlib

def hash_password(password: str) -> str:
    """
    Simple password hashing using SHA-256.
    Note: For production, use bcrypt or Argon2.
    """
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    """
    return hash_password(plain_password) == hashed_password
