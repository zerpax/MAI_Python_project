from sqlalchemy import create_engine, text
from sqlmodel import SQLModel, Session
from config import DATABASE_URL

from tasks import predict
import pandas as pd
import numpy as np
from database import get_session
from models import History, Scammers
import random

def generate_random_ip():
    return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"


# Функция для чтения CSV, обработки данных и записи в базу
def process_and_store_data(csv_file: str, db_url: str):
    # Чтение CSV файла
    df = pd.read_csv(csv_file)
    df = df.drop(columns=["target"])

    # Создаем соединение с базой данных
    engine = create_engine(db_url)

    with Session(engine) as session:
        session.exec(text("ALTER SEQUENCE history_id_seq START WITH 1"))
        session.exec(text("ALTER SEQUENCE scammers_id_seq START WITH 1"))
        session.commit()
        for _, row in df.iterrows():
            # Создаем список истории для текущей строки
            history_data = [
                {"site_id": row[f"site{i}"], "time": row[f"time{i}"]}
                for i in range(1, 11)
                if pd.notna(row[f"site{i}"]) and pd.notna(row[f"time{i}"])
            ]

            # Создаем запись в таблице
            record = History(
                ip_address=generate_random_ip(),
                history=history_data
            )
            session.add(record)

        # Сохраняем все изменения
        session.commit()


# Пример использования
if __name__ == "__main__":
    csv_file_path = "dataset/train_sessions.csv"  # Путь к вашему CSV файлу
    database_url = "postgresql://postgres:gangball08@localhost:5432/postgres"

    process_and_store_data(csv_file_path, database_url)

    predict.delay()