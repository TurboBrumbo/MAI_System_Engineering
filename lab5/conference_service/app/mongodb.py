from pymongo import ASCENDING
from bson import ObjectId
from typing import List, Dict, Optional
import os
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from datetime import datetime

class MongoDBConferences:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGODB_URI", "mongodb://mongo:1@mongodb:27017/"))
        self.db = self.client["conference_db"]
        self.conferences = self.db["conferences"]

        self.conferences.create_index([("title", ASCENDING)], unique=True)
        self.conferences.create_index([("start_date", ASCENDING)])
        self.conferences.create_index([("end_date", ASCENDING)])

    def init_mongodb(self):
        try:
            self.conferences.delete_many({})

            test_conferences = [
                {
                    "title": "Young&&Yandex Data Science meeting",
                    "description": "рекрутинг молодых специалистов по машинному обучению",
                    "start_date": datetime(2025, 3, 24),
                    "end_date": datetime(2025, 3, 25),
                    "participants": [],
                    "created_at": datetime.utcnow()
                },
                {
                    "title": "MAI Avia-Hackathon",
                    "description": "разработка продакшн-системы в интересах IT компаний",
                    "start_date": datetime(2024, 12, 15),
                    "end_date": datetime(2024, 12, 18),
                    "participants": [],
                    "created_at": datetime.utcnow()
                }
            ]

            self.conferences.insert_many(test_conferences)
            print("Тестовые данные конференций успешно загружены")
        except Exception as e:
            print(f"Ошибка при загрузке тестовых данных: {e}")

    def get_conference(self, conference_id: str) -> Optional[Dict]:
        try:
            return self.conferences.find_one({"_id": ObjectId(conference_id)})
        except:
            return None

    def get_conferences(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        return list(self.conferences.find().skip(skip).limit(limit))

    def search_by_title(self, title_part: str, skip: int = 0, limit: int = 100) -> List[Dict]:
        return list(self.conferences.find(
            {"title": {"$regex": title_part, "$options": "i"}}
        ).skip(skip).limit(limit))

    def create_conference(self, conference_data: Dict) -> str:
        try:
            conference_data["created_at"] = datetime.utcnow()
            result = self.conferences.insert_one(conference_data)
            return str(result.inserted_id)
        except DuplicateKeyError:
            raise ValueError("Conference with this title already exists")

    def update_conference(self, conference_id: str, update_data: Dict) -> bool:
        result = self.conferences.update_one(
            {"_id": ObjectId(conference_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0

    def delete_conference(self, conference_id: str) -> bool:
        result = self.conferences.delete_one({"_id": ObjectId(conference_id)})
        return result.deleted_count > 0

    def get_upcoming_conferences(self, limit: int = 5) -> List[Dict]:
        return list(self.conferences.find(
            {"start_date": {"$gt": datetime.utcnow()}}
        ).sort("start_date", ASCENDING).limit(limit))


conferences_db = MongoDBConferences()
conferences_db.init_mongodb()