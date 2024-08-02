from pydantic import BaseModel
from typing import Optional

class JobDescriptionCreate(BaseModel):
    prompt: str

class JobDescriptionUpdate(BaseModel):
    prompt: Optional[str] = None
    job_description: Optional[str] = None

class JobDescriptionResponse(BaseModel):
    id: int
    prompt: str
    job_description: str