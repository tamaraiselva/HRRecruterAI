import os
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# MongoDB setup
client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
database = client.HRRecruterAI
Resource_collection = database.get_collection("ResourceAI")

# MySQL setup
mysql_uri = os.getenv("MYSQL_URI")
engine = create_engine(mysql_uri)