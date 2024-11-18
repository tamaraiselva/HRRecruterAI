from fastapi import FastAPI
from routes.job import router as jd_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="JD-RecruiterAI")

origins = [
    "*",
    "http://localhost",
    "http://localhost:8082" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jd_router, prefix="/api/v1/jd", tags=["Job Descriptions"])