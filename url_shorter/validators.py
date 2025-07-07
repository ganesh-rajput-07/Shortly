from pydantic import BaseModel, EmailStr
from typing import Optional

class Forauth(BaseModel):
    email : EmailStr
    password : str

class urlshort(BaseModel) :
    originalUrl : str
    shortenUrl : Optional[str]
