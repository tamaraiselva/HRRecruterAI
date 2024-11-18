from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse
from models.user import User, UpdateUser
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

user = APIRouter(prefix="/api/v1/user", tags=['User'])

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


@user.get('/')
async def find_all_users():
    users = list(conn.local.user.find())
    if users:
        logger.info(f"Found {len(users)} users")
        return JSONResponse(status_code=status.HTTP_200_OK, content=usersEntity(users))
    else:
        logger.warning("No users found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users found"
        )
    
@user.post('/')
async def create_user(user: User):
    try:
        logger.info(f"Attempting to create user with email: {user.email}")
        existing_user = conn.local.user.find_one({"email": user.email})
        if existing_user:
            logger.error(f"User with email {user.email} already exists")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        
        user_dict = user.dict()
        user_dict['id'] = get_next_sequence_value('userid')   # Assign sequential ID
        user_dict['password'] = hashpw(user.password.encode('utf-8'), gensalt()).decode('utf-8')
        user_dict["role"]="user"
        user_dict["whatsapp_api_token"]=None
        user_dict["whatsapp_cloud_number_id"]=None
        conn.local.user.insert_one(user_dict)
        logger.info(f"User created with ID: {user_dict['id']}")
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=userEntity(user_dict))
    
    except InvalidUserException as e:
        logger.error(f"InvalidUserException: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise InvalidUserException(detail=str(e))

@user.put('/{id}')
async def update_user(id: int, update_user: UpdateUser):
    logger.info(f"Updating user with ID: {id}")
    existing_user = conn.local.user.find_one({"id": id})
    if not existing_user:
        logger.error(f"User with ID {id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} not found"
        )

    user_data = update_user.dict(exclude_unset=True)
    if 'password' in user_data:
        user_data['password'] = hashpw(user_data['password'].encode('utf-8'), gensalt()).decode('utf-8')

    # Create User model to validate the updated data
    updated_user = UpdateUser(**{**existing_user, **user_data})
    
    result = conn.local.user.update_one(
        {"id": id},
        {"$set": user_data}
    )

    if result.modified_count == 1:
        logger.info(f"User with ID {id} updated successfully")
        updated_user = conn.local.user.find_one({"id": id})
        return JSONResponse(status_code=status.HTTP_200_OK, content=userEntity(updated_user))
    else:
        logger.error(f"Failed to update user with ID: {id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user"
        )

@user.get('/{id}')
async def get_user(id: int):
    user = conn.local.user.find_one({"id": id})
    if user:
        logger.info(f"User with ID {id} found")
        return JSONResponse(status_code=status.HTTP_200_OK, content=userEntity(user))
    else:
        logger.warning(f"User with ID {id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} not found"
        )

@user.delete('/{id}')
async def delete_user(id: int):
    result = conn.local.user.delete_one({"id": id})

    if result.deleted_count == 1:
        logger.info(f"User with ID {id} deleted successfully")
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": f"User with id {id} deleted successfully"})
    else:
        logger.error(f"User with ID {id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} not found"
        )
