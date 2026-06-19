from collections.abc import Mapping

import jwt

from app.config import settings


def create_access_token(user_id: int) -> str:
    payload: dict[str, str] = {"sub": str(user_id)}
    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> Mapping[str, object]:
    return jwt.decode(  # type: ignore[no-any-return]
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
    )
