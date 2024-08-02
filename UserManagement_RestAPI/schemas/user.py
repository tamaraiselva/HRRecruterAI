# schemas/user.py

import pymongo

def userEntity(item) -> dict:
    return {
        "id": item["id"],  # Assuming "id" is stored as an integer in MongoDB
        "name": item["name"],
        "email": item["email"],
        "mobile_number":item["mobile_number"],
        "location":item["location"],
        "role":item["role"],
        # "password": item["password"]
        "whatsapp_api_token": item["whatsapp_api_token"],
        "whatsapp_cloud_number_id": item["whatsapp_cloud_number_id"]
    }

def usersEntity(entity):
    if isinstance(entity, pymongo.collection.Collection):
        entity = list(entity.find())  # Convert Collection to list of documents
    return [userEntity(item) for item in entity]
