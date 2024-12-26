from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import update
from sqlmodel import select
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker, AsyncSession
from sqlalchemy.sql import text
from typing import AsyncGenerator, List
import jwt
import bcrypt
from datetime import timedelta
from fastapi.middleware.cors import CORSMiddleware
from config import DATABASE_URL, SECRET_KEY, ALGORITHM
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from tasks import predict  # Celery-задача
import logging


from models import *

#database setup
database_URL = DATABASE_URL #связать с базой данных проекта
engine = create_async_engine(database_URL,  echo=True)
Session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with Session() as session:
        yield session



#JWT
key = SECRET_KEY #change later
jwt_algorithm = ALGORITHM
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


@app.on_event("startup")
async def create_db_and_tables():
    scheduler.add_job(
        predict.delay,
        trigger=CronTrigger(hour=0, minute=0),  # Ежедневно в полночь
        id='daily_predict_task',
        replace_existing=True
    )
    scheduler.start()
    logger.info("APScheduler запущен")
    async with engine.begin() as conn:
        await conn.execute(text('CREATE SCHEMA IF NOT EXISTS user_data'))
        await conn.run_sync(SQLModel.metadata.create_all)


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
    logger.info("APScheduler остановлен")
    await engine.dispose()


@app.post('/register/', response_model=UsersPublic)# register user
async def register(user: UsersRegister, session: Session = Depends(get_session)):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user.password.encode(), salt)

    user_data = user.dict(exclude={"password"})
    user_data["hashed_password"] = hashed_password
    db_user = Users(**user_data)

    db_user = Users.model_validate(db_user)# need to add support for invalid data

    session.add(db_user) #check if exists
    await session.commit()
    await session.refresh(db_user)
    return db_user


@app.get('/register/')
def register():
    pass


@app.get('/login/')
def login():
    pass


@app.post('/login/')
async def login(user_input: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    query = select(Users).where(Users.email == user_input.username)
    result = await session.execute(query)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_email = user.email
    db_password = user.hashed_password

    if not bcrypt.checkpw(user_input.password.encode(), db_password.encode()):
        raise HTTPException(status_code=400, detail='Wrong password')

    token_expiration = timedelta(days=7)
    token = jwt.encode(
        {
            'id': user.id,
            'email': db_email,
            'exp': datetime.now(UTC) + token_expiration
        },
        key,
        algorithm=jwt_algorithm
    )

    return {"token": token, "token_type": "bearer"}


def decode_jwt(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, key, algorithms=[jwt_algorithm])
        email = payload['email']
        role = payload['role']
        if email is None:
            raise HTTPException(status_code=401, detail='Invalid token')
        return {'email': email, 'role': role}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token expired')
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail='Invalid token')


@app.get('/user/', response_model=UsersPublic) #для тестирования jwt токена
async def get_user(user_info=Depends(decode_jwt), session: Session = Depends(get_session)):
    query = select(Users).where(Users.email == user_info['email'])
    result = await session.execute(query)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    return user


@app.post('/history/', response_model=VisitPublic)
async def post_history(visit_data: VisitPublic, session: AsyncSession = Depends(get_session)):
    ip_address = visit_data.ip_address

    # Проверяем, есть ли запись для данного IP
    query = select(History).where(History.ip_address == ip_address)
    result = await session.execute(query)
    existing_history = result.scalars().first()
    new_visit = VisitPublic(ip_address=ip_address, site_id=visit_data.site_id, time=visit_data.time)

    if not existing_history:
        # Если записи нет, создаем новую
        new_history = History(ip_address=ip_address, history=[{'site': visit_data.site_id, 'time': visit_data.time}])
        session.add(new_history)
        await session.commit()
        await session.refresh(new_history)  # Обновляем объект после сохранения
        return new_visit
    else:
        # Если запись есть, обновляем историю
        if len(existing_history.history) >= 10:
            existing_history.history.pop(0)  # Удаляем самый старый элемент
        existing_history.history.append({'site': visit_data.site_id, 'time': visit_data.time})  # Добавляем новый элемент
        query = update(History).where(History.ip_address == ip_address).values(history=existing_history.history)
        # Обновляем запись в базе данных
        await session.execute(query)
        await session.commit()
        await session.refresh(existing_history)  # Обновляем объект после сохранения
        return new_visit


@app.get('/scammers/', response_model=List[ScammersPublic])
def get_scammers(session: Session = Depends(get_session)):
    query = select(Scammers.ip_address)  # Выбираем только ip_address
    result = session.execute(query)
    scammers = [row[0] for row in result.fetchall()]  # Преобразуем результат в список ip_address
    return scammers


