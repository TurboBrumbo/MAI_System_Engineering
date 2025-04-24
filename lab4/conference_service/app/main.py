from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from bson import ObjectId

from .mongodb import conferences_db
from . import schemas
from .crud import get_current_user
from .schemas import ConferenceUpdate

app = FastAPI(title="Сервис конференций (MongoDB)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://user_service:8000/token")

@app.post("/conferences/", response_model=schemas.Conference)
async def create_conference(
    conference: schemas.ConferenceCreate,
    token: str = Depends(oauth2_scheme)
):
    await get_current_user(token)
    conference_data = conference.dict()
    conference_id = conferences_db.create_conference(conference_data)
    return {**conference_data, "id": conference_id}

@app.get("/conferences/", response_model=List[schemas.Conference])
def list_conferences(
    skip: int = 0,
    limit: int = 100,
    title: Optional[str] = None,
    upcoming: bool = False
):
    if upcoming:
        return conferences_db.get_upcoming_conferences(limit=limit)
    if title:
        return conferences_db.search_by_title(title, skip=skip, limit=limit)
    return conferences_db.get_conferences(skip=skip, limit=limit)

@app.get("/conferences/{conference_id}", response_model=schemas.Conference)
async def get_conference(conference_id: str):
    try:
        _ = ObjectId(conference_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid conference ID format")

    conference = conferences_db.get_conference(conference_id)
    if not conference:
        raise HTTPException(status_code=404, detail="Conference not found")
    return conference

@app.put("/conferences/{conference_id}", response_model=schemas.Conference)
async def update_conference(
    conference_id: str,
    conference: schemas.ConferenceUpdate,
    token: str = Depends(oauth2_scheme)
):
    await get_current_user(token)
    if not conferences_db.update_conference(conference_id, conference.dict()):
        raise HTTPException(status_code=404, detail="Conference not found")
    return conferences_db.get_conference(conference_id)

@app.delete("/conferences/{conference_id}")
async def delete_conference(
    conference_id: str,
    token: str = Depends(oauth2_scheme)
):
    await get_current_user(token)
    if not conferences_db.delete_conference(conference_id):
        raise HTTPException(status_code=404, detail="Conference not found")
    return {"message": "Conference deleted successfully"}

@app.get("/conferences/{conference_id}/participants", response_model=List[str])
def get_participants(conference_id: str):
    conference = conferences_db.get_conference(conference_id)
    if not conference:
        raise HTTPException(status_code=404, detail="Conference not found")
    return conference.get("participants", [])

@app.get("/")
async def health_check():
    return {"status": "ok", "database": "mongodb"}