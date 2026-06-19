from passlib.context import CryptContext  # type: ignore[import-untyped]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)  # type: ignore[no-any-return]


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)  # type: ignore[no-any-return]
