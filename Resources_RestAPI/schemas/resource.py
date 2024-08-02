from pydantic import BaseModel
from typing import List, Optional

class ResourceCreate(BaseModel):
    job_description: str

class ResourceUpdate(BaseModel):
    job_description: Optional[str] = None

class ResourceResponse(BaseModel):
    id: int
    resource: List[str]
