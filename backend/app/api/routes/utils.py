from datetime import UTC, datetime, timedelta

from app.core import security
from app.core.security import settings
import jwt


def generate_password_reset_token(email:str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.now(UTC)
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp":exp, "nbf":now, "sub":email},
        settings.SECRET_KEY,
        algorithm=security.ALGORITHM
    )

    return encoded_jwt

