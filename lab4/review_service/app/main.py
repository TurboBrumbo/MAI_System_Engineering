from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

from .mongodb import reviews_db
from . import schemas
from .crud import get_current_user
from .schemas import ReviewUpdate

app = FastAPI(title="Сервис докладов (MongoDB)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://user_service:8000/token")

@app.post("/reviews/", response_model=schemas.Review)
async def create_review(
    review: schemas.ReviewCreate,
    token: str = Depends(oauth2_scheme)
):
    try:
        current_user = await get_current_user(token)
        review_data = review.model_dump()
        review_data["author_id"] = str(current_user.id)
        review_id = reviews_db.create_review(review_data)
        return {**review_data, "id": review_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/reviews/", response_model=List[schemas.Review])
def list_reviews(
        conference_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
):
    if conference_id:
        return reviews_db.get_reviews_by_conference(conference_id)
    return reviews_db.get_reviews(skip=skip, limit=limit)

@app.get("/reviews/{review_id}", response_model=schemas.Review)
def get_review(review_id: str):
    review = reviews_db.get_review(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@app.put("/reviews/{review_id}", response_model=schemas.Review)
async def update_review(
        review_id: str,
        review: schemas.ReviewUpdate,
        token: str = Depends(oauth2_scheme)
):
    current_user = await get_current_user(token)
    review_data = review.dict()
    existing_review = reviews_db.get_review(review_id)

    if not existing_review:
        raise HTTPException(status_code=404, detail="Review not found")
    if existing_review["author_id"] != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to update this review")

    if reviews_db.update_review(review_id, review_data):
        return {**review_data, "id": review_id}
    raise HTTPException(status_code=500, detail="Failed to update review")

@app.delete("/reviews/{review_id}")
async def delete_review(
        review_id: str,
        token: str = Depends(oauth2_scheme)
):
    current_user = await get_current_user(token)
    review = reviews_db.get_review(review_id)

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review["author_id"] != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this review")

    if reviews_db.delete_review(review_id):
        return {"message": "Review deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete review")

@app.get("/reviews/conference/{conference_id}/stats")
def get_review_stats(conference_id: str):
    return reviews_db.get_review_stats(conference_id)

@app.get("/")
async def health_check():
    return {"status": "ok", "database": "mongodb"}