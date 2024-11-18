from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse
from models.members import Members,UpdateMember
from config.db import conn
from schemas.members import memberEntity, membersEntity
from exceptions.exceptions import InvalidUserException
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

members = APIRouter(prefix="/api/v1/member", tags=['Panel_Members'])

def get_next_sequence_value(sequence_name):
    seq = conn.local.counters.find_one_and_update(
        {"_id": sequence_name},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return seq["sequence_value"]


@members.get('/')
async def find_all_panel_members():
    members = list(conn.local.members.find())
    if members:
        logger.info(f"Found {len(members)} members")
        return JSONResponse(status_code=status.HTTP_200_OK, content=membersEntity(members))
    else:
        logger.warning("No panel members found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No panel members found"
        )
    
@members.post('/')
async def create_panel_member(member: Members):
    try:
        logger.info(f"Attempting to create panel member with email: {member.email}")
        existing_member = conn.local.members.find_one({"email": member.email})
        if existing_member:
            logger.error(f"Panel member with email {member.email} already exists")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Panel member with this email already exists"
            )
        
        member_dict = member.dict()
        member_dict['id'] = get_next_sequence_value('memberid')   # Assign sequential ID
        conn.local.members.insert_one(member_dict)
        logger.info(f"Panel member created with ID: {member_dict['id']}")
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=memberEntity(member_dict))
    
    except InvalidUserException as e:
        logger.error(f"InvalidUserException encountered: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Error creating panel member: {str(e)}")
        raise InvalidUserException(detail=str(e))

@members.put('/{id}')
async def update_panel_member(id: int, update_member: UpdateMember):
    logger.info(f"Updating panel member with ID: {id}")
    existing_member = conn.local.members.find_one({"id": id})
    if not existing_member:
        logger.error(f"Panel Member with ID {id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Panel Member with id {id} not found"
        )

    member_data = update_member.dict(exclude_unset=True)


    # Create Member model to validate the updated data
    updated_member = UpdateMember(**{**existing_member, **member_data})
    
    result = conn.local.members.update_one(
        {"id": id},
        {"$set": member_data}
    )

    if result.modified_count == 1:
        logger.info(f"Panel member with ID {id} updated successfully")
        updated_member = conn.local.members.find_one({"id": id})
        return JSONResponse(status_code=status.HTTP_200_OK, content=memberEntity(updated_member))
    else:
        logger.error(f"Failed to update panel member with ID {id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update member"
        )

@members.get('/{id}')
async def get_panel_member(id: int):
    member = conn.local.members.find_one({"id": id})
    if member:
        logger.info(f"Panel member with ID {id} found")
        return JSONResponse(status_code=status.HTTP_200_OK, content=memberEntity(member))
    else:
        logger.warning(f"Panel Member with ID {id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Panel Member with id {id} not found"
        )

@members.delete('/{id}')
async def delete_panel_member(id: int):
    result = conn.local.members.delete_one({"id": id})

    if result.deleted_count == 1:
        logger.info(f"Panel member with ID {id} deleted successfully")
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": f"Panel Member with id {id} deleted successfully"})
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Panel Member with id {id} not found"
        )
