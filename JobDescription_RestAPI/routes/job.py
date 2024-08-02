from fastapi import APIRouter, HTTPException, status
from typing import List
from schemas.job_schemas import JobDescriptionResponse, JobDescriptionCreate, JobDescriptionUpdate
from services.job_services import get_all_jds, get_jd, create_jd, update_jd, delete_jd

router = APIRouter()

@router.get("/", response_model=List[JobDescriptionResponse])
async def read_all_jds():
    return await get_all_jds()

@router.get("/{id}", response_model=JobDescriptionResponse)
async def read_jd(id: int):
    jd = await get_jd(id)
    if jd is None:
        raise HTTPException(status_code=404, detail="Job Description not found")
    return jd

@router.post("/", response_model=JobDescriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_jd_route(jd: JobDescriptionCreate):
    return await create_jd(jd)

@router.put("/{id}", response_model=JobDescriptionResponse)
async def update_jd_route(id: int, jd_update: JobDescriptionUpdate):
    jd = await update_jd(id, jd_update)
    if jd is None:
        raise HTTPException(status_code=404, detail="Job Description not found")
    return jd

@router.delete("/{id}", response_model=dict)
async def delete_jd_route(id: int):
    success = await delete_jd(id)
    if not success:
        raise HTTPException(status_code=404, detail="Job Description not found")
    return {"message": "Job Description deleted successfully"}