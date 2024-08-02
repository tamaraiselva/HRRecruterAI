import os
import logging
import json
from typing import List, Optional
from langchain_huggingface import HuggingFaceEndpoint
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from config.db import Resource_collection
from models.resource import Resource, ResourceCreate, ResourceUpdate
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.output_parsers import StrOutputParser
from fastapi import HTTPException

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Set environment variables
huggingface_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
if not huggingface_token:
    logger.error("Huggingface API token not found in environment variables.")
    raise HTTPException(status_code=500, detail="Huggingface API token not set in environment variables")

os.environ['HUGGINGFACEHUB_API_TOKEN'] = huggingface_token
mysql_uri = os.getenv("MYSQL_URI")
if not mysql_uri:
    logger.error("MySQL URI not found in environment variables.")
    raise HTTPException(status_code=500, detail="MySQL URI not set in environment variables")

# Initialize LLM
repo_id1 = "mistralai/Mistral-7B-Instruct-v0.2"
try:
    llm1 = HuggingFaceEndpoint(repo_id=repo_id1, temperature=0.5, max_length=200)
except Exception as e:
    logger.error(f"Invalid Huggingface API token: {e}")
    raise HTTPException(status_code=500, detail="Huggingface token invalid")

# Function to extract keywords from job description
def extract_keywords(job_description_text):
    keyword_template = """Extract the following details from the job description:
                Experience: The candidate's experience in years. Output as an integer.
                Skills: List the skills mentioned in the job description using single words only (e.g., Java, SQL). Separate skills with commas.
                Qualification: List the qualifications mentioned, separated by commas.
                Format the output as JSON with keys: Experience, Skills, Qualification. Include only the information specified in {text}.
                text: {text}
            """

    keyword_prompt = ChatPromptTemplate.from_template(template=keyword_template)
    parser = StrOutputParser()
    chain = keyword_prompt | llm1 | parser

    response = chain.invoke({"text": job_description_text})

    start_idx = response.find("{")
    end_idx = response.rfind("}") + 1
    json_response = response[start_idx:end_idx]

    try:
        output_dict = json.loads(json_response)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed: {e}")
        output_dict = {"Experience": 0, "Skills": [], "Qualification": []}

    Experience = output_dict.get("Experience", 0)
    Skills = output_dict.get("Skills", [])
    Qualification = output_dict.get("Qualification", [])

    return Experience, Skills, Qualification

# CRUD operations
async def create_resource(resource_data: ResourceCreate) -> Resource:
    Experience, Skills, Qualification = extract_keywords(resource_data.job_description)
    # Ensure Skills is a list
    if isinstance(Skills, str):
        Skills = [s.strip() for s in Skills.split(',')]
        
    if isinstance(Qualification, str):
        Qualification = [q.strip() for q in Qualification.split(',')]
    candidates = filter_candidates(Experience, Skills, Qualification)

    id = await Resource_collection.count_documents({}) + 1
    resource_dict = {
        "id": id,
        "job_description": resource_data.job_description,
        "skills": Skills,
        "qualification": Qualification,
        "experience": Experience,
        "resource": [candidates]
    }

    await Resource_collection.insert_one(resource_dict)
    return Resource(**resource_dict)

async def get_all_resources() -> List[Resource]:
    resources = await Resource_collection.find().to_list(1000)
    return [Resource(**resource) for resource in resources]

async def get_resource_by_id(id: int) -> Optional[Resource]:
    resource = await Resource_collection.find_one({"id": id})
    if resource:
        return Resource(**resource)
    return None

async def update_resource(id: int, resource_update: ResourceUpdate) -> Optional[Resource]:
    update_data = {k: v for k, v in resource_update.dict().items() if v is not None}
    if "job_description" in update_data:
        Experience, Skills, Qualification = extract_keywords(update_data["job_description"])
        update_data.update({
            "experience": Experience,
            "skills": Skills,
            "qualification": Qualification
        })
    result = await Resource_collection.update_one({"id": id}, {"$set": update_data})
    if result.modified_count:
        return await get_resource_by_id(id)
    return None

async def delete_resource(id: int) -> bool:
    result = await Resource_collection.delete_one({"id": id})
    return result.deleted_count > 0

# Candidate filtering function
def filter_candidates(Experience, Skills, Qualification):
    db = SQLDatabase.from_uri(mysql_uri)
    query_prompt_template = """Generate an SQL query to find candidates with the following criteria:
        Experience greater than {experience}.
        Skills including {skills}.
        Qualifications including {qualification}.
        Output the results with the following fields: id, name, email, mobile number, Education, Experience.
        """
    skills_str = ", ".join(Skills) if Skills else "any"
    qualification_str = ", ".join(Qualification) if Qualification else "any"

    query_prompt_query = query_prompt_template.format(
        experience=Experience,
        skills=skills_str,
        qualification=qualification_str
    )

    query_chain = create_sql_query_chain(llm=llm1, db=db)
    try:
        sql_query = query_chain.invoke({"question": query_prompt_query})
        execute_query_tool = QuerySQLDataBaseTool(db=db)
        filtered_candidates = execute_query_tool.invoke(sql_query)
    except Exception as e:
        logger.error(f"Error while filtering candidates: {e}")
        filtered_candidates = []

    return filtered_candidates