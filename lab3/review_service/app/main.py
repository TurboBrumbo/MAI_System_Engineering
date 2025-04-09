from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Optional
from jose import jwt, JWTError
from fastapi.middleware.cors import CORSMiddleware
from fastapi import status

app = FastAPI(
    title="Сервис докладов",
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

fake_reviews_db = []
next_review_id = 1

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

@app.post("/reviews/", response_model=Review)
async def create_review(
    review: ReviewCreate,
    token: str = Depends(oauth2_scheme)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    global next_review_id
    new_review = Review(
        id=next_review_id,
        title=review.title,
        author=review.author,
        description=review.description,
        conference_id=review.conference_id
    )
    fake_reviews_db.append(new_review.dict())
    next_review_id += 1
    return new_review

@app.get("/reviews/", response_model=List[Review])
async def read_reviews(conference_id: Optional[int] = None):
    if conference_id is not None:
        return [review for review in fake_reviews_db if review["conference_id"] == conference_id]
    return fake_reviews_db

@app.get("/reviews/{review_id}", response_model=Review)
async def read_review(review_id: int):
    for review in fake_reviews_db:
        if review["id"] == review_id:
            return review
    raise HTTPException(status_code=404, detail="Review not found")