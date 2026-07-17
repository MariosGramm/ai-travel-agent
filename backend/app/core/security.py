
from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import settings
import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher


password_hash = PasswordHash(
    (
        Argon2Hasher(),
        BcryptHasher(),
    )
)

ALGORITHM = "HS256"

def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    """
    Method for jwt token signature and encoding.
    """
    expire = datetime.now(UTC) + expires_delta
    to_encode = {"exp":expire, "sub":str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def verify_password(plain_password:str, hashed_password: str) -> tuple[bool, str | None]:
    """
    Verifies a given password using the hash of the original password (stored in the database).
    """
    return password_hash.verify_and_update(plain_password, hashed_password)

def get_password_hash(password:str) -> str:
    """
    Method for password hashing.
    """
    return password_hash.hash(password)

