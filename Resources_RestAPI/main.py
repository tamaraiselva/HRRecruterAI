from fastapi import FastAPI
from routes.resource import router as resource_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Resource API")

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

app.include_router(resource_router, prefix="/api/v1/resource", tags=["Job Resources"])