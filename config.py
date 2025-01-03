import os
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")
BROKER_URL = os.getenv("BROKER_URL")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

YOOMONEY_TOKEN = os.getenv("YOOMONEY_TOKEN")
RECEIVER = os.getenv("RECEIVER")
# ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))