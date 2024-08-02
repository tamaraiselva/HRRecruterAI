from motor.motor_asyncio import AsyncIOMotorClient
import os

client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
database = client.HRRecruterAI
job_description_collection = database.get_collection("job_descriptions")
