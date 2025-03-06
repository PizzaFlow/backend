from dotenv import load_dotenv
import os
from fastapi_mail import FastMail, ConnectionConfig

load_dotenv('.env')

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
JWT_EXPIRE_TIME = os.getenv("JWT_EXPIRE_TIME")

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=os.getenv("MAIL_PORT"),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_FROM_NAME="PizzaFlow",
    MAIL_STARTTLS=True,  # Замена для MAIL_TLS
    MAIL_SSL_TLS=False,  # Замена для MAIL_SSL
    USE_CREDENTIALS=True,  # Указывает, использовать ли логин/пароль
    VALIDATE_CERTS=True  # Проверять ли сертификаты
)