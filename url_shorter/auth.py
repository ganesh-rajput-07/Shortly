from jose import jwt
from datetime import datetime, timedelta

SECRETE_KEY = "this is mine secrete key"
ALGORITHM = 'HS256'
ACCESS_TIME_IN_MINUTES = 30

def create_token(data: dict, expires_on: timedelta = None ):
    to_encode = data.copy()
    expires_at = datetime.utcnow() + (expires_on or timedelta(minutes=ACCESS_TIME_IN_MINUTES))
    to_encode.update({'exp':expires_at})
    return jwt.encode(to_encode, SECRETE_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    return jwt.decode(token, SECRETE_KEY, algorithms=[ALGORITHM])