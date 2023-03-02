from passlib.context import CryptContext

from config.config import PASSWORD_SALT


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password + PASSWORD_SALT, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password + PASSWORD_SALT)
