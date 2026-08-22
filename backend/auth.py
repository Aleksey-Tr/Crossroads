from passlib.context import CryptContext
from config import SECRET_KEY, ALGORITHM
import jwt
import bcrypt
from models import UserModel

hasher = CryptContext(schemes='bcrypt')

def password_to_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password_to_check: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password_to_check.encode(), hashed_password.encode())

def create_jwt(user: UserModel) -> str:
    payload = user.model_dump() #по хорошему добавить срок действия jwt
    return jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)

def verify_jwt(jwt_token: str) -> UserModel|None:
    try:
        user = jwt.decode(jwt=jwt_token, key=SECRET_KEY, algorithms=ALGORITHM)
        return UserModel.model_validate(user)
    except:
        return None
    