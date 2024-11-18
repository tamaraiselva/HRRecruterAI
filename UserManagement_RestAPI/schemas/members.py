import pymongo

def memberEntity(item) -> dict:
    return {
        "id": item["id"],  # Assuming "id" is stored as an integer in MongoDB
        "name": item["name"],
        "email": item["email"],
        "mobile_number":item["mobile_number"],
        "location":item["location"]
    }

def membersEntity(entity):
    if isinstance(entity, pymongo.collection.Collection):
        entity = list(entity.find())  # Convert Collection to list of documents
    return [memberEntity(item) for item in entity]