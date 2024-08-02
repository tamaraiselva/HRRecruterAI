from pydantic import BaseModel, validator
from exceptions.exceptions import InvalidUserException

class PasswordResetRequest(BaseModel):
    new_password: str

    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise InvalidUserException(detail='Password must be at least 8 characters long')
        if not v[0].isupper():
            raise InvalidUserException(detail='Password must start with an uppercase letter')
        if not any(char.isdigit() for char in v):
            raise InvalidUserException(detail='Password must contain at least one digit')
        if not any(char.islower() for char in v):
            raise InvalidUserException(detail='Password must contain at least one lowercase letter')
        if not any(char in "!@#$%^&*()_+-=" for char in v):
            raise InvalidUserException(detail='Password must contain at least one special character')
        return v
