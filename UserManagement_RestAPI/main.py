from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from routes.user import user
from exceptions.exceptions import InvalidUserException
from routes.login_router import login_router
from routes.admin_router import admin
from routes.members_router import members
from routes.password_reset import password_reset_router
from config.db import conn
import bcrypt
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from routes.response_router import response_router

app = FastAPI(title="User Management")

origins = [
    "*",
    "http://localhost",
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.exception_handler(InvalidUserException)
async def invalid_user_handler(request: Request, exc: InvalidUserException):
    logger.warning(f"InvalidUserException: {exc.detail} - Request: {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

app.include_router(user)
app.include_router(admin)
app.include_router(members)
app.include_router(login_router)
app.include_router(password_reset_router)
app.include_router(response_router)


def get_next_sequence_value(sequence_name):
    seq = conn.local.counters.find_one_and_update(
        {"_id": sequence_name},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return seq["sequence_value"]


# Password hashing setup
def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

@app.on_event("startup")
def startup():
    admin_id=get_next_sequence_value('userid')
    admin_name = "Admin"
    admin_email = "admin@gmail.com"
    admin_mobile_number = 8907654321
    admin_password = "Admin@12345"
    admin_location = "Bangalore"
    admin_role = "admin"
    admin_whatsapp_api_token=None
    admin_whatsapp_cloud_number_id=None

    existing_admin = conn.local.user.find_one({"email": admin_email})

    if not existing_admin:
        hashed_password = get_password_hash(admin_password)
        admin = {
            "id":admin_id,
            "name": admin_name,
            "email": admin_email,
            "mobile_number": admin_mobile_number,
            "location": admin_location,
            "password": hashed_password,
            "role": admin_role,
            "whatsapp_api_token": admin_whatsapp_api_token,
            "whatsapp_cloud_number_id": admin_whatsapp_cloud_number_id
        }
        conn.local.user.insert_one(admin)
        logger.info(f"Admin created with email {admin['email']}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8083)
