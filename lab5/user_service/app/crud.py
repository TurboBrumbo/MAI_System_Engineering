from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.encoders import jsonable_encoder

from .models import User
from .schemas import UserCreate, TokenData
from .database import get_password_hash, SessionLocal, SECRET_KEY, ALGORITHM, pwd_context, redis_client
from typing import List, Optional

import pickle

CACHE_EXPIRE = 300

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user(db: Session, user_id: int) -> Optional[User]:
    cache_key = f"user:{user_id}"
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return pickle.loads(cached_data)

    user = db.query(User).filter(User.id == user_id).first()
    if user:
        redis_client.setex(cache_key, CACHE_EXPIRE, pickle.dumps(user))
    return user


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        hashed_password=get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_data: dict) -> Optional[User]:
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None

    for key, value in user_data.items():
        if key == 'password':
            setattr(db_user, 'hashed_password', get_password_hash(value))
        else:
            setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)

    cache_key = f"user:{user_id}"
    redis_client.setex(cache_key, CACHE_EXPIRE, pickle.dumps(db_user))
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return False

    db.delete(db_user)
    db.commit()

    cache_key = f"user:{user_id}"
    redis_client.delete(cache_key)
    return True


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username=username)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(SessionLocal)
):
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
        token_data = TokenData(username=username)
    except jwt.JWTError:
        raise credentials_exception

    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user