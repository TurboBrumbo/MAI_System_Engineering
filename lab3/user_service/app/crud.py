from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .models import User, Conference, Review
from .schemas import UserCreate, ConferenceCreate, ReviewCreate, TokenData
from .database import get_password_hash, SessionLocal, SECRET_KEY, ALGORITHM, pwd_context
from typing import List, Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        hashed_password=hashed_password
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
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return False

    db.delete(db_user)
    db.commit()
    return True


def get_conference(db: Session, conference_id: int) -> Optional[Conference]:
    return db.query(Conference).filter(Conference.id == conference_id).first()


def get_conferences(db: Session, skip: int = 0, limit: int = 100) -> List[Conference]:
    return db.query(Conference).offset(skip).limit(limit).all()


def create_conference(db: Session, conference: ConferenceCreate) -> Conference:
    db_conference = Conference(
        title=conference.title,
        description=conference.description,
        start_date=conference.start_date,
        end_date=conference.end_date
    )
    db.add(db_conference)
    db.commit()
    db.refresh(db_conference)
    return db_conference


def update_conference(db: Session, conference_id: int, conference_data: dict) -> Optional[Conference]:
    db_conference = db.query(Conference).filter(Conference.id == conference_id).first()
    if not db_conference:
        return None

    for key, value in conference_data.items():
        setattr(db_conference, key, value)

    db.commit()
    db.refresh(db_conference)
    return db_conference


def delete_conference(db: Session, conference_id: int) -> bool:
    db_conference = db.query(Conference).filter(Conference.id == conference_id).first()
    if not db_conference:
        return False

    db.delete(db_conference)
    db.commit()
    return True


def get_review(db: Session, review_id: int) -> Optional[Review]:
    return db.query(Review).filter(Review.id == review_id).first()


def get_reviews(db: Session, skip: int = 0, limit: int = 100) -> List[Review]:
    return db.query(Review).offset(skip).limit(limit).all()


def get_reviews_by_conference(db: Session, conference_id: int) -> List[Review]:
    return db.query(Review).filter(Review.conference_id == conference_id).all()


def create_review(db: Session, review: ReviewCreate, author_id: int) -> Review:
    db_review = Review(
        title=review.title,
        description=review.description,
        conference_id=review.conference_id,
        author_id=author_id
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


def update_review(db: Session, review_id: int, review_data: dict) -> Optional[Review]:
    db_review = db.query(Review).filter(Review.id == review_id).first()
    if not db_review:
        return None

    for key, value in review_data.items():
        setattr(db_review, key, value)

    db.commit()
    db.refresh(db_review)
    return db_review


def delete_review(db: Session, review_id: int) -> bool:
    db_review = db.query(Review).filter(Review.id == review_id).first()
    if not db_review:
        return False

    db.delete(db_review)
    db.commit()
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