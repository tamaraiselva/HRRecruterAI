from fastapi import APIRouter, HTTPException
from typing import List, Optional
from models.resource import Resource, ResourceCreate, ResourceUpdate, ResourceResponse
from services.resource import create_resource, get_all_resources, get_resource_by_id, update_resource, delete_resource

router = APIRouter()

@router.post("/", response_model=ResourceResponse)
async def create(resource_data: ResourceCreate):
    return await create_resource(resource_data)

@router.get("/", response_model=List[ResourceResponse])
async def read_all():
    return await get_all_resources()

@router.get("/{id}", response_model=Optional[ResourceResponse])
async def read(id: int):
    resource = await get_resource_by_id(id)
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource

@router.put("/{id}", response_model=Optional[Resource])
async def update(id: int, resource_update: ResourceUpdate):
    resource = await update_resource(id, resource_update)
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource

@router.delete("/{id}", response_model=dict)
async def delete(id: int):
    success = await delete_resource(id)
    if not success:
        raise HTTPException(status_code=404, detail="Resource not found")
    return {"message": "deleted successfully"}
