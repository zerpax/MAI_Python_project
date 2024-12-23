from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import select
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker, AsyncSession
from typing import AsyncGenerator, List
import jwt
import bcrypt
from datetime import timedelta
from fastapi.middleware.cors import CORSMiddleware


from models import *

#database setup
database_URL = "postgresql+asyncpg://postgres:rj40Vt02lB60z@localhost:5432/{}" #связать с базой данных проекта
engine = create_async_engine(database_URL,  echo=True)
Session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with Session() as session:
        yield session



#JWT
key = "pogchamp" #change later
jwt_algorithm = 'HS256'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


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


@app.get('/user/', response_model=UsersPublic)
async def get_user(user_info=Depends(decode_jwt), session: Session = Depends(get_session)):
    query = select(Users).where(Users.email == user_info['email'])
    result = await session.execute(query)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    return user


