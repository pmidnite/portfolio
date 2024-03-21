# config.py
import os

MONGO_URI = "mongodb://localhost:27017/portfolio"
SECRET_KEY = "Access Secured"
JWT_SECRET_KEY = "JWT ACCESS KEY"

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or SECRET_KEY
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or JWT_SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    MONGO_URI =  os.environ.get('MONGO_URI') or MONGO_URI
