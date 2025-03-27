from pydantic import BaseModel
from typing import Optional

class Review(BaseModel):
    id: int
    title: str
    author: str
    description: Optional[str] = None
    conference_id: Optional[int] = None

class ReviewCreate(BaseModel):
    title: str
    author: str
    description: Optional[str] = None
    conference_id: Optional[int] = None