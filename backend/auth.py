from passlib.context import CryptContext

hasher = CryptContext(schemes='bcrypt')

def password_to_hash(password: str) -> str:
    return hasher.hash(password)

def verify_password(password_to_check: str, hashed_password: str) -> bool:
    return hasher.verify(password_to_check, hashed_password)
