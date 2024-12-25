from celery import Celery
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sqlalchemy import delete
from sqlmodel import select
from database import get_session
from models import History, Scammers
from config import BROKER_URL


def preprocessing_data(raw_data: pd.DataFrame) -> pd.DataFrame:
    _test = pd.DataFrame()
    sites = raw_data[['site%s' % i for i in range(1, 11)]].fillna(0).astype(int).values
    times = raw_data[['time%s' % i for i in range(1, 11)]]

    for td_index in range(1, 10):
        _test['time_diff{}'.format(td_index)] = (
                pd.to_datetime(times['time{}'.format(td_index + 1)])
                - pd.to_datetime(times['time{}'.format(td_index)])
        ).dt.total_seconds().fillna(0)

    _test['time_of_session'] = np.sum(_test, axis=1)
    _test['hour'] = pd.to_datetime(times['time1']).dt.hour
    _test['dow'] = pd.to_datetime(times['time1']).dt.dayofweek
    _test['month'] = pd.to_datetime(times['time1']).dt.month
    _test['unique_sites'] = [len(np.unique(session[session != 0])) for session in sites]

    _test['target_hour'] = np.where(
        ((_test['hour'] >= 12) & (_test['hour'] <= 13)) | ((_test['hour'] >= 16) & (_test['hour'] <= 18)), 1, 0)

    _test['target_dow'] = np.where(((_test['dow'] == 5) | (_test['dow'] == 6)), 1, 0)

    _test['target_month'] = np.where((_test['month'] >= 5) & (_test['month'] <= 8), 0, 1)
    return _test


app = Celery('tasks', broker=BROKER_URL, backend='rpc://')

model = CatBoostClassifier()
model.load_model("IT_project/catboost_model.cbm")


@app.task
async def predict():
    async with get_session() as session:
        # Получаем данные из таблицы History
        result = await session.execute(select(History))
        result = result.scalars().all()

        # Преобразуем данные в список словарей
        data = []
        user_ips = []
        for row in result:
            history = row.history  # Список словарей из 10 элементов
            user_ips.append(row.ip_address)
            flattened_row = {"id": row.id}
            for i, record in enumerate(history, start=1):
                flattened_row[f"site{i}"] = record.get("site_id")
                flattened_row[f"time{i}"] = record.get("timestamp")
            data.append(flattened_row)

        # Преобразуем в DataFrame
        df = pd.DataFrame(data)

        # Подготовка данных для модели
        prepared_data = preprocessing_data(df)

        # Предсказания модели
        predictions = model.predict(prepared_data)
        scam_ips = [user_ip for user_ip, prediction in zip(user_ips, predictions) if prediction == 1]

        # Удаление всех записей из History
        await session.execute(delete(History))

        # Получение существующих IP в таблице Scammers
        result = await session.execute(
            select(Scammers.ip_address).filter(Scammers.ip_address.in_(scam_ips))
        )
        existing_scam_ips = {row[0] for row in result.fetchall()}

        # Формируем список новых IP-адресов, которых еще нет в таблице
        new_ips = [Scammers(ip_address=ip) for ip in scam_ips if ip not in existing_scam_ips]

        # Добавляем новые IP
        session.add_all(new_ips)

        # Сохраняем изменения
        await session.commit()

        return new_ips
