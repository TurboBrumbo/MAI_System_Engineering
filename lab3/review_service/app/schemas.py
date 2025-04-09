from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    disabled: bool

    class Config:
        from_attributes = True

class ConferenceBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime

class ConferenceCreate(ConferenceBase):
    pass

class Conference(ConferenceBase):
    id: int

    class Config:
        from_attributes = True

class ReviewBase(BaseModel):
    title: str
    description: Optional[str] = None
    conference_id: int

class ReviewCreate(ReviewBase):
    pass

class Review(ReviewBase):
    id: int
    author_id: int

    class Config:
        from_attributes = True