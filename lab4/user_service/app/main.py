from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import SessionLocal, engine, Base
from . import schemas
from .crud import (
    create_user,
    create_access_token,
    update_user,
    delete_user,
    authenticate_user,
    get_current_active_user
)

app = FastAPI(title="Сервис авторизации пользователей")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user

@app.post("/users/", response_model=schemas.User)
def create_new_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return create_user(db=db, user=user)

@app.put("/users/{user_id}", response_model=schemas.User)
def update_existing_user(
    user_id: int,
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    updated_user = update_user(db, user_id=user_id, user_data=user.dict())
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@app.delete("/users/{user_id}")
def delete_existing_user(user_id: int, db: Session = Depends(get_db)):
    if not delete_user(db, user_id=user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

@app.get("/")
async def root():
    return {"message": "User Service is working!"}