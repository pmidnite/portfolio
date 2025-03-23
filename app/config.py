# config.py
import os


SECRET_KEY = "Access Secured"
JWT_SECRET_KEY = "JWT ACCESS KEY"

SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{username}:{password}@{hostname}/{databasename}".format(
    username="root",
    password="Passw0rd!23",
    hostname="localhost",
    databasename="portfolio",
    )

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or SECRET_KEY
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or JWT_SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_POOL_RECYCLE = 299
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Outlook/hotmail Mail configs
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'abc@gmail.com'
    MAIL_PASSWORD = 'App Password'
    MAIL_RECIPIENT = 'xyz@gmail.com'
