from fastapi import APIRouter, HTTPException
from pymongo.collection import Collection
from config.db import conn
from models.login import LoginRequest
from bcrypt import checkpw

login_router = APIRouter(prefix="/api/v1/login",tags=['Login'])

@login_router.post('/')
async def login(login_request: LoginRequest):
    user_collection: Collection = conn.local.user
    user = user_collection.find_one({"email": login_request.email})
    
    if user and checkpw(login_request.password.encode('utf-8'), user["password"].encode('utf-8')):
        return {"message": "Login Successful", "user_id": int(user["id"]),"user_role":str(user["role"])}  # Adjust response as needed
    elif user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    else:
        raise HTTPException(status_code=404, detail="Username not found")
    



