import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from passlib.context import CryptContext
import time

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:1@postgres:5432/conference_db")

def wait_for_db():
    engine = create_engine(DATABASE_URL)
    attempts = 0
    while attempts < 10:
        try:
            with engine.connect() as conn:
                print("✅ База данных готова")
                return True
        except OperationalError as e:
            attempts += 1
            print(f"⌛ Ожидание базы данных (attempt {attempts}/10)")
            time.sleep(5)
    raise Exception("❌ Не удалось подключиться к базе данных за 10 попыток")


def init_db():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            full_name VARCHAR(100),
            email VARCHAR(100),
            hashed_password VARCHAR(100) NOT NULL,
            disabled BOOLEAN DEFAULT FALSE
        );

        CREATE TABLE IF NOT EXISTS conferences (
            id SERIAL PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            description TEXT,
            start_date TIMESTAMP NOT NULL,
            end_date TIMESTAMP NOT NULL
        );

        CREATE TABLE IF NOT EXISTS reviews (
            id SERIAL PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            description TEXT,
            conference_id INTEGER REFERENCES conferences(id),
            author_id INTEGER REFERENCES users(id)
        );

        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
        CREATE INDEX IF NOT EXISTS idx_users_full_name ON users(full_name);
        CREATE INDEX IF NOT EXISTS idx_conferences_title ON conferences(title);
        CREATE INDEX IF NOT EXISTS idx_reviews_conference_id ON reviews(conference_id);
        
        INSERT INTO users (username, full_name, email, hashed_password)
        VALUES 
            ('admin', 'Maxim Krasavin', 'turbobrumbo@gmail.com', :password1),
            ('teacher', 'Ilya Irbitskiy', 'myhamster@mail.ru@mail.ru', :password2)
        ON CONFLICT (username) DO NOTHING
        """), {
            'password1': get_password_hash("secret"),
            'password2': get_password_hash("aboba")
        })
        conn.commit()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully")