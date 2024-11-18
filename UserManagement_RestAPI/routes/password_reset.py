from fastapi import APIRouter, HTTPException
from pymongo.collection import Collection
from config.db import conn
from models.password_reset import PasswordResetRequest
from bcrypt import hashpw, gensalt
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

password_reset_router = APIRouter(prefix="/api/v1/password_reset", tags=['Password Reset'])


@password_reset_router.put('/{email}')
async def reset_password(email: str, request: PasswordResetRequest):
    logger.info(f"Password reset attempt for email: {email}")
    
    try:
        user_collection: Collection = conn.local.user
        user = user_collection.find_one({"email": email})
        
        if user:
            new_hashed_password = hashpw(request.new_password.encode('utf-8'), gensalt()).decode('utf-8')
            result = user_collection.update_one(
                {"email": email},
                {"$set": {"password": new_hashed_password}}
            )
            
            if result.modified_count == 1:
                logger.info(f"Password reset successful for user: {email}")
                return {"message": "Password reset successful"}
            else:
                logger.error(f"Password reset failed during update for user: {email}")
                raise HTTPException(status_code=500, detail="Password reset failed")
        else:
            logger.warning(f"Password reset attempt for non-existent email: {email}")
            raise HTTPException(status_code=404, detail="User with the given email not found")
    
    except Exception as e:
        logger.error(f"Error during password reset for {email}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")