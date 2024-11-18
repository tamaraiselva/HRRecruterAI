from fastapi import APIRouter, HTTPException
from pymongo.collection import Collection
from config.db import conn
from models.login import LoginRequest
from bcrypt import checkpw
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

login_router = APIRouter(prefix="/api/v1/login",tags=['Login'])

@login_router.post('/')
async def login(login_request: LoginRequest):
    logger.info(f"Login attempt for email: {login_request.email}")
    user_collection: Collection = conn.local.user
    user = user_collection.find_one({"email": login_request.email})
    
    if user and checkpw(login_request.password.encode('utf-8'), user["password"].encode('utf-8')):
        logger.info(f"User {login_request.email} logged in successfully.")
        return {"message": "Login Successful", "user_id": int(user["id"]),"user_role":str(user["role"])}  # Adjust response as needed
    elif user:
        logger.warning(f"Failed login attempt for user {login_request.email}: Invalid email or password.")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    else:
        logger.error(f"Login attempt for non-existent user: {login_request.email}")
        raise HTTPException(status_code=404, detail="Username not found")
    



