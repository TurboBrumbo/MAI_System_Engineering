from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Optional
from jose import jwt, JWTError
from fastapi.middleware.cors import CORSMiddleware
from fastapi import status

app = FastAPI(
    title="Сервис конференций",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.get("/")
async def root():
    return {"message": "Review Service is working!"}

SECRET_KEY = "secret"
ALGORITHM = "HS256"

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

fake_conferences_db = []
next_conference_id = 1

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://user_service:8000/token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username

@app.post("/conferences/", response_model=Conference)
async def create_conference(
    conference: ConferenceCreate,
    token: str = Depends(oauth2_scheme)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    global next_conference_id
    new_conference = Conference(
        id=next_conference_id,
        title=conference.title,
        description=conference.description,
        start_date=conference.start_date,
        end_date=conference.end_date
    )
    fake_conferences_db.append(new_conference.dict())
    next_conference_id += 1
    return new_conference

@app.get("/conferences/", response_model=List[Conference])
async def read_conferences():
    return fake_conferences_db

@app.get("/conferences/{conference_id}", response_model=Conference)
async def read_conference(conference_id: int):
    for conference in fake_conferences_db:
        if conference["id"] == conference_id:
            return conference
    raise HTTPException(status_code=404, detail="Conference not found")