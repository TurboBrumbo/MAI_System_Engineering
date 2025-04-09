from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from .database import SessionLocal
from . import schemas
from .crud import (
    get_conference,
    get_conferences,
    create_conference,
    get_current_user
)

app = FastAPI(title="Сервис конференций")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://user_service:8000/token")

@app.post("/conferences/", response_model=schemas.Conference)
async def create_new_conference(
    conference: schemas.ConferenceCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    await get_current_user(token, db)
    return create_conference(db=db, conference=conference)

@app.get("/conferences/", response_model=List[schemas.Conference])
def read_conferences(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_conferences(db, skip=skip, limit=limit)

@app.get("/conferences/{conference_id}", response_model=schemas.Conference)
def read_conference(conference_id: int, db: Session = Depends(get_db)):
    conference = get_conference(db, conference_id=conference_id)
    if not conference:
        raise HTTPException(status_code=404, detail="Conference not found")
    return conference

@app.get("/")
async def root():
    return {"message": "Conference Service is working!"}