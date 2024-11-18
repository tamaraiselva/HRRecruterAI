from pydantic import BaseModel, EmailStr, validator
from exceptions.exceptions import InvalidUserException
import re

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


    @validator('email')
    def validate_email(cls, v):
        # Regular expression to validate email format
        email_pattern = r'^[\w._%+-]+@[a-zA-Z]+\.[a-zA-Z]+$'
        if not re.match(email_pattern, v):
            raise InvalidUserException(detail='Invalid email format')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise InvalidUserException(detail='Password must be at least 8 characters long')
        if not any(char.isupper() for char in v):
            raise InvalidUserException(detail='Password must contain at least one uppercase letter')
        if not any(char.isdigit() for char in v):
            raise InvalidUserException(detail='Password must contain at least one digit')
        if not any(char.islower() for char in v):
            raise InvalidUserException(detail='Password must contain at least one lowercase letter')
        if not any(char in "!@#$%^&*()_+-=" for char in v):
            raise InvalidUserException(detail='Password must contain at least one special character')
        return v
