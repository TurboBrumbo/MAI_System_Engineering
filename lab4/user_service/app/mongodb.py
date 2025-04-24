from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import time


MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://mongo:1@localhost:27017/")
DB_NAME = "conference_db"
COLLECTION_NAME = "conferences"


def wait_for_mongodb():
    attempts = 0
    while attempts < 10:
        try:
            client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            client.server_info()
            print("✅ MongoDB готова")
            return client
        except ConnectionFailure as e:
            attempts += 1
            print(f"⌛ Ожидание MongoDB (попытка {attempts}/10)")
            time.sleep(5)
    raise Exception("❌ Не удалось подключиться к MongoDB за 10 попыток")


client = wait_for_mongodb()
db = client[DB_NAME]
conferences_collection = db[COLLECTION_NAME]


conferences_collection.create_index([("title", ASCENDING)], unique=True)
conferences_collection.create_index([("start_date", ASCENDING)])
conferences_collection.create_index([("end_date", ASCENDING)])


def init_mongodb():
    conferences_collection.delete_many({})

    test_conferences = [
        {
            "title": "Young&&Yandex Data Science meeting",
            "description": "рекрутинг молодых специалистов по машинному обучению",
            "start_date": datetime(2025, 3, 24),
            "end_date": datetime(2025, 3, 25),
            "participants": []
        },
        {
            "title": "MAI Avia-Hackathon",
            "description": "разработка продакшн-системы в интересах IT компаний",
            "start_date": datetime(2024, 12, 15),
            "end_date": datetime(2024, 12, 18),
            "participants": []
        }
    ]

    conferences_collection.insert_many(test_conferences)


def get_conference(conference_id: str) -> Optional[Dict[str, Any]]:
    return conferences_collection.find_one({"_id": conference_id})


def get_conferences(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    return list(conferences_collection.find().skip(skip).limit(limit))


def create_conference(conference_data: Dict[str, Any]) -> str:
    result = conferences_collection.insert_one(conference_data)
    return str(result.inserted_id)


def update_conference(conference_id: str, conference_data: Dict[str, Any]) -> bool:
    result = conferences_collection.update_one(
        {"_id": conference_id},
        {"$set": conference_data}
    )
    return result.modified_count > 0


def delete_conference(conference_id: str) -> bool:
    result = conferences_collection.delete_one({"_id": conference_id})
    return result.deleted_count > 0


def search_conferences_by_title(title_part: str) -> List[Dict[str, Any]]:
    return list(conferences_collection.find(
        {"title": {"$regex": title_part, "$options": "i"}}
    ))


def add_participant(conference_id: str, user_id: str) -> bool:
    result = conferences_collection.update_one(
        {"_id": conference_id},
        {"$addToSet": {"participants": user_id}}
    )
    return result.modified_count > 0