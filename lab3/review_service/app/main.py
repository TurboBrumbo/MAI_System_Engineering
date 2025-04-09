from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

from .database import SessionLocal
from . import schemas
from .crud import (
    get_review,
    get_reviews,
    get_reviews_by_conference,
    create_review,
    get_current_user
)

app = FastAPI(title="Сервис докладов")

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

@app.post("/reviews/", response_model=schemas.Review)
async def create_new_review(
    review: schemas.ReviewCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(token, db)
    return create_review(db=db, review=review, author_id=current_user.id)

@app.get("/reviews/", response_model=List[schemas.Review])
def read_all_reviews(
    conference_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    if conference_id:
        return get_reviews_by_conference(db, conference_id=conference_id)
    return get_reviews(db)

@app.get("/reviews/{review_id}", response_model=schemas.Review)
def read_single_review(review_id: int, db: Session = Depends(get_db)):
    db_review = get_review(db, review_id=review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    return db_review

@app.get("/")
async def root():
    return {"message": "Review Service is working!"}