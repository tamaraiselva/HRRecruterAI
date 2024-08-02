from pydantic import BaseModel

class JobDescription(BaseModel):
    id: int
    prompt: str
    job_description: str
