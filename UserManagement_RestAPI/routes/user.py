from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse
from models.user import User, UpdateUser
from config.db import conn
from schemas.user import userEntity, usersEntity
from bcrypt import hashpw, gensalt
from exceptions.exceptions import InvalidUserException

user = APIRouter(prefix="/api/v1/user", tags=['User'])

def get_next_sequence_value(sequence_name):
    seq = conn.local.counters.find_one_and_update(
        {"_id": sequence_name},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return seq["sequence_value"]

@user.get('/')
async def find_all_users():
    users = list(conn.local.user.find())
    if users:
        return JSONResponse(status_code=status.HTTP_200_OK, content=usersEntity(users))
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users found"
        )

@user.post('/')
async def create_user(user: User):
    try:
        existing_user = conn.local.user.find_one({"email": user.email})
        if existing_user:
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
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=userEntity(user_dict))
    
    except InvalidUserException as e:
        raise e
    except Exception as e:
        raise InvalidUserException(detail=str(e))

@user.put('/{id}')
async def update_user(id: int, update_user: UpdateUser):
    existing_user = conn.local.user.find_one({"id": id})
    if not existing_user:
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
        updated_user = conn.local.user.find_one({"id": id})
        return JSONResponse(status_code=status.HTTP_200_OK, content=userEntity(updated_user))
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user"
        )

@user.get('/{id}')
async def get_user(id: int):
    user = conn.local.user.find_one({"id": id})
    if user:
        return JSONResponse(status_code=status.HTTP_200_OK, content=userEntity(user))
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} not found"
        )

@user.delete('/{id}')
async def delete_user(id: int):
    result = conn.local.user.delete_one({"id": id})

    if result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": f"User with id {id} deleted successfully"})
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} not found"
        )
