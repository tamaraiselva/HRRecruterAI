from pydantic import BaseModel, EmailStr, validator
from exceptions.exceptions import InvalidUserException
from typing import Optional
import re

class Members(BaseModel):
    name: str
    email: EmailStr
    mobile_number: int  # Mobile number as integer
    location: str

    @validator('name')
    def name_length_and_capitalization(cls, v):
        if len(v) > 15:
            raise InvalidUserException(detail='Name must be 15 characters or less')
        if not v[0].isupper():
            raise InvalidUserException(detail='Name must start with a capital letter')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        # Regular expression to validate email format
        email_pattern = r'^[\w._%+-]+@[a-zA-Z]+\.[a-zA-Z]+$'
        if not re.match(email_pattern, v):
            raise InvalidUserException(detail='Invalid email format')
        return v

    @validator('mobile_number')
    def validate_mobile_number(cls, v):
        mobile_str = str(v)
        if len(mobile_str) != 10 or not mobile_str.isdigit():
            raise InvalidUserException(detail='Mobile number must be exactly 10 digits')
        return v


class UpdateMember(BaseModel):
    name: str = None
    email: EmailStr = None
    mobile_number: int = None
    location: str = None

    @validator('name')
    def name_length_and_capitalization(cls, v):
        if len(v) > 15:
            raise InvalidUserException(detail='Name must be 15 characters or less')
        if not v[0].isupper():
            raise InvalidUserException(detail='Name must start with a capital letter')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        # Regular expression to validate email format
        email_pattern = r'^[\w._%+-]+@[a-zA-Z]+\.[a-zA-Z]+$'
        if not re.match(email_pattern, v):
            raise InvalidUserException(detail='Invalid email format')
        return v

    @validator('mobile_number')
    def validate_mobile_number(cls, v):
        mobile_str = str(v)
        if len(mobile_str) != 10 or not mobile_str.isdigit():
            raise InvalidUserException(detail='Mobile number must be exactly 10 digits')
        return v
    