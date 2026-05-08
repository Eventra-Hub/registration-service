import bcrypt
import jwt

from datetime import datetime, timedelta

from app.core.config import settings


def hash_password(password: str):

    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()


def verify_password(password, hashed):

    return bcrypt.checkpw(
        password.encode(),
        hashed.encode()
    )


def create_token(user_id: str):

    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(days=1)
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm="HS256"
    )


def verify_token(token: str):

    try:

        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"]
        )

        return payload

    except jwt.PyJWTError:

        return None
