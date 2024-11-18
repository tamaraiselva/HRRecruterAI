from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse
from models.admin import Admin
from config.db import conn
from schemas.user import userEntity, usersEntity
from bcrypt import hashpw, gensalt
from exceptions.exceptions import InvalidUserException
import random
import string
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

admin = APIRouter(prefix="/api/v1/admin", tags=['Admin'])

def get_next_sequence_value(sequence_name):
    seq = conn.local.counters.find_one_and_update(
        {"_id": sequence_name},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return seq["sequence_value"]


def generate_password(length: int = 12) -> str:
    if length < 8:
        raise ValueError("Password length should be at least 8 characters.")
    
    # Ensure the password has at least one of each character type
    characters = {
        "uppercase": random.choice(string.ascii_uppercase),
        "lowercase": random.choice(string.ascii_lowercase),
        "digits": random.choice(string.digits),
        "special": random.choice(string.punctuation)
    }
    
    # Fill the rest of the password length with random choices from all character types
    all_characters = string.ascii_letters + string.digits + string.punctuation
    remaining_length = length - len(characters)
    password = ''.join(random.choices(all_characters, k=remaining_length))
    
    # Combine and shuffle to ensure randomness
    password_list = list(characters.values()) + list(password)
    random.shuffle(password_list)
    
    return ''.join(password_list)

@admin.post('/')
async def create_admin_user(user: Admin):
    try:
        logger.info(f"Attempting to create admin user with email: {user.email}")
        existing_user = conn.local.user.find_one({"email": user.email})
        if existing_user:
            logger.error(f"User with email {user.email} already exists")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        generated_password = generate_password(8)  # Ensure at least 8 characters
        logger.info(f"Generated password for user {user.email}")
        
        user_dict = user.dict()
        user_dict['id'] = get_next_sequence_value('userid')   # Assign sequential ID
        user_dict['password'] = hashpw(generated_password.encode('utf-8'), gensalt()).decode('utf-8')
        user_dict["role"]="user"
        user_dict["whatsapp_api_token"]=None
        user_dict["whatsapp_cloud_number_id"]=None
        conn.local.user.insert_one(user_dict)
        logger.info(f"Admin user created with ID: {user_dict['id']}")
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=userEntity(user_dict))
    
    except InvalidUserException as e:
        logger.error(f"InvalidUserException encountered: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        raise InvalidUserException(detail=str(e))
