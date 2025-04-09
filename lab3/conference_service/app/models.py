from pydantic import BaseModel
from typing import Optional

class Conference(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    start_date: str
    end_date: str

class ConferenceCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: str
    end_date: str