from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, Text, TIMESTAMP, ForeignKey

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    full_name = Column(String(100))
    email = Column(String(100))
    hashed_password = Column(String(100))
    disabled = Column(Boolean, default=False)

class Conference(Base):
    __tablename__ = "conferences"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    start_date = Column(TIMESTAMP, nullable=False)
    end_date = Column(TIMESTAMP, nullable=False)

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    conference_id = Column(Integer, ForeignKey('conferences.id'))
    author_id = Column(Integer, ForeignKey('users.id'))