from fastapi import APIRouter, BackgroundTasks, Response, HTTPException
from pymongo.collection import Collection
from config.db import conn
from datetime import datetime

response_router = APIRouter()

def store_response_in_db(job_id: str, email: str, response: str):
    response_collection: Collection = conn.local.candidate_responses

    # Document structure
    response_document = {
        "job_id": job_id,
        "email": email,
        "response": response.lower(),
        "timestamp": datetime.utcnow()
    }

    # Insert response into MongoDB
    result = response_collection.insert_one(response_document)
    if not result.acknowledged:
        raise Exception("Failed to save response.")

@response_router.get("/api/v1/response/{job_id}/{email}")
async def capture_response(job_id: str, email: str, response: str, background_tasks: BackgroundTasks):
    if response.lower() not in ["yes", "no"]:
        raise HTTPException(status_code=400, detail="Invalid response. Use 'yes' or 'no'.")

    background_tasks.add_task(store_response_in_db, job_id, email, response)

    # Return an empty response with status 204 (No Content)
    return Response(status_code=204)
