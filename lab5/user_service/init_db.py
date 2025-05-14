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
            print(f"⌛ Ожидание базы данных (попытка {attempts}/10)")
            time.sleep(5)
    raise Exception("❌ Не удалось подключиться к базе данных за 10 попыток")


def init_db():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS reviews CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS conferences CASCADE;"))
        conn.commit()

        conn.execute(text("""
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            full_name VARCHAR(100),
            email VARCHAR(100),
            hashed_password VARCHAR(100) NOT NULL,
            disabled BOOLEAN DEFAULT FALSE
        );
        """))
        conn.commit()

        conn.execute(text("""
        CREATE INDEX idx_users_username ON users(username);
        CREATE INDEX idx_users_full_name ON users(full_name);
        """))
        conn.commit()

        conn.execute(text("""
        INSERT INTO users (username, full_name, email, hashed_password)
        VALUES 
            ('admin', 'Maxim Krasavin', 'turbobrumbo@gmail.com', :password1),
            ('teacher', 'Ilya Irbitskiy', 'myhamster@mail.ru', :password2)
        ON CONFLICT (username) DO NOTHING;
        """), {
            'password1': get_password_hash("secret"),
            'password2': get_password_hash("aboba")
        })
        conn.commit()


if __name__ == "__main__":
    wait_for_db()
    init_db()