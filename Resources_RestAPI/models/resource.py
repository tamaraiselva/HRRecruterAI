from pydantic import BaseModel
from typing import List, Optional

class Resource(BaseModel):
    id: int
    job_description: str
    skills: List[str]
    qualification: List[str]
    experience: int
    resource: List[str]

class ResourceCreate(BaseModel):
    job_description: str

class ResourceUpdate(BaseModel):
    job_description: Optional[str] = None
    skills: Optional[List[str]] = None
    qualification: Optional[List[str]] = None
    experience: Optional[int] = None
    resource: Optional[List[str]] = None

class ResourceResponse(BaseModel):
    id: int
    resource: List[str]
