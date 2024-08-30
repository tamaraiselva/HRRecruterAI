# services/job_services.py

from typing import List, Optional
from fastapi import HTTPException
from config.db import job_description_collection
from models.job_models import JobDescription
from schemas.job_schemas import JobDescriptionCreate, JobDescriptionUpdate
from langchain_huggingface import HuggingFaceEndpoint
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
import logging

load_dotenv()

os.environ['HUGGINGFACEHUB_API_TOKEN'] = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with a public model repo id
repo_id = "mistralai/Mistral-7B-Instruct-v0.2"

try:
    llm = HuggingFaceEndpoint(repo_id=repo_id, temperature=0.5, max_length=200)
except Exception as e:
    logger.error(f"Error initializing HuggingFaceEndpoint: {e}")
    raise HTTPException(status_code=500, detail=f"Huggingface token invalid: {e}")

def jd_helper(jd) -> dict:
    return {
        "id": jd["id"],
        "prompt": jd["prompt"],
        "job_description": jd["job_description"]
    }

async def get_all_jds() -> List[JobDescription]:
    jds = await job_description_collection.find().to_list(1000)
    return [JobDescription(**jd_helper(jd)) for jd in jds]

async def get_jd(id: int) -> Optional[JobDescription]:
    jd = await job_description_collection.find_one({"id": id})
    if jd:
        return JobDescription(**jd_helper(jd))
    return None

async def create_jd(jd_data: JobDescriptionCreate) -> JobDescription:
    job_desc_prompt_template = """Create a job description based on the following details:
            job Title
            Company Introduction
            Job Description
            Responsibilities
            Skills and Qualifications
            Include only the information specified in {user_input}. Do not add any additional details or commentary.Output the results with the following fields : job Title, Company Introduction, Job Description, Responsibilities, Skills and Qualifications.
            text: {user_input}
        """
    job_desc_prompt = ChatPromptTemplate.from_template(job_desc_prompt_template)
    try:
        job_desc_chain = LLMChain(llm=llm, prompt=job_desc_prompt)
    except Exception as e:
        logger.error(f"Error creating LLMChain: {e}")
        raise HTTPException(status_code=500, detail="Bad response for Huggingface key")

    try:
        job_description_result = job_desc_chain.invoke({"user_input": jd_data.prompt})
        job_description_text = job_description_result.get('text', "")
    except Exception as e:
        logger.error(f"Error invoking LLMChain: {e}")
        raise HTTPException(status_code=500, detail="Error generating job description")

    new_id = await job_description_collection.count_documents({}) + 1
    
    jd_dict = {
        "id": new_id,
        "prompt": jd_data.prompt,
        "job_description": job_description_text
    }
    await job_description_collection.insert_one(jd_dict)
    return JobDescription(**jd_dict)

async def update_jd(id: int, jd_data: JobDescriptionUpdate) -> Optional[JobDescription]:
    jd = await job_description_collection.find_one({"id": id})
    if not jd:
        return None

    update_data = {}

    if jd_data.prompt:
        job_desc_prompt_template = """Create a job description based on the following details:
            job Title
            Company Introduction
            Job Description
            Responsibilities
            Skills and Qualifications
            Include only the information specified in {user_input}. Do not add any additional details or commentary.Output the results with the following fields : job Title, Company Introduction, Job Description, Responsibilities, Skills and Qualifications.
            text: {user_input}
        """

        # Initialize the prompt with the provided user input
        job_desc_prompt = ChatPromptTemplate.from_template(job_desc_prompt_template)

        # Create a chain with the LLM and prompt
        try:
            job_desc_chain = LLMChain(llm=llm, prompt=job_desc_prompt)
        except Exception as e:
            logger.error(f"Error creating LLMChain: {e}")
            raise HTTPException(status_code=500, detail="Bad response for Huggingface key")

        # Run the chain with the user input and get the result
        try:
            job_description_result = job_desc_chain.invoke({"user_input": jd_data.prompt})
            job_description_text = job_description_result.get('text', "")
        except Exception as e:
            logger.error(f"Error invoking LLMChain: {e}")
            raise HTTPException(status_code=500, detail="Error generating job description")

        update_data["prompt"] = jd_data.prompt
        update_data["job_description"] = job_description_text
    elif jd_data.job_description:
        update_data["job_description"] = jd_data.job_description

    if update_data:
        await job_description_collection.update_one({"id": id}, {"$set": update_data})
        jd = await job_description_collection.find_one({"id": id})
        return JobDescription(**jd_helper(jd))

    return JobDescription(**jd_helper(jd))
async def delete_jd(id: int) -> bool:
    result = await job_description_collection.delete_one({"id": id})
    return result.deleted_count > 0
