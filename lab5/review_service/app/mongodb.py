from pymongo import MongoClient, ASCENDING, DESCENDING
from bson import ObjectId
from datetime import datetime
from typing import List, Dict, Optional
import os
from pymongo.errors import DuplicateKeyError


class MongoDBReviews:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGODB_URI", "mongodb://mongo:1@mongodb:27017/"))
        self.db = self.client["conference_db"]
        self.reviews = self.db["reviews"]

        self.reviews.create_index([("conference_id", ASCENDING)])
        self.reviews.create_index([("author_id", ASCENDING)])
        self.reviews.create_index([("status", ASCENDING)])
        self.reviews.create_index([("created_at", DESCENDING)])

    def init_mongodb(self):
        try:
            self.reviews.delete_many({})
            test_reviews = [
                {
                    "title": "Выступление спикера Яндекс",
                    "description": "Немного душно",
                    "conference_id": str(ObjectId()),
                    "author_id": "2",
                    "status": "approved",
                    "created_at": datetime.utcnow()
                },
                {
                    "title": "Нейросети в 2025",
                    "description": "Обзор современных моделей",
                    "conference_id": str(ObjectId()),
                    "author_id": "1",
                    "status": "approved",
                    "created_at": datetime.utcnow()
                }
            ]
            self.reviews.insert_many(test_reviews)
            print("Тестовые доклады загружены")
        except Exception as e:
            print(f"Ошибка загрузки тестовых данных: {e}")

    def get_review(self, review_id: str) -> Optional[Dict]:
        try:
            return self.reviews.find_one({"_id": ObjectId(review_id)})
        except:
            return None

    def get_reviews(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        return list(self.reviews.find().skip(skip).limit(limit))

    def get_reviews_by_conference(self, conference_id: str) -> List[Dict]:
        return list(self.reviews.find({"conference_id": conference_id}))

    def create_review(self, review_data: Dict) -> str:
        try:
            review_data["created_at"] = datetime.utcnow()
            result = self.reviews.insert_one(review_data)
            return str(result.inserted_id)
        except DuplicateKeyError as e:
            raise ValueError("Review creation error") from e

    def update_review(self, review_id: str, update_data: Dict) -> bool:
        result = self.reviews.update_one(
            {"_id": ObjectId(review_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0

    def delete_review(self, review_id: str) -> bool:
        result = self.reviews.delete_one({"_id": ObjectId(review_id)})
        return result.deleted_count > 0

    def get_review_stats(self, conference_id: str) -> Dict:
        pipeline = [
            {"$match": {"conference_id": conference_id}},
            {"$group": {
                "_id": None,
                "count": {"$sum": 1},
                "latest": {"$max": "$created_at"}
            }}
        ]
        result = list(self.reviews.aggregate(pipeline))
        return result[0] if result else {"count": 0, "latest": None}


reviews_db = MongoDBReviews()
reviews_db.init_mongodb()