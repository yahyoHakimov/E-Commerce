from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.core.config import settings

pwd_context = CryptContext(schemes = ["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)
    
def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)

    to_encode.update({"exp": expire})

    encode_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm = settings.JWT_ALGORITHM)

    return encode_jwt
    
def decode_access_token(token: str) -> dict | None:
    try:
        decode_token = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms = [settings.JWT_ALGORITHM]
        )

        return decode_token
    
    except JWTError:
        return None
