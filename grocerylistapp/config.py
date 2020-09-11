from decouple import config

import os
from sqlalchemy import create_engine

class Config:
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = "sqlite:///site.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = config('EMAIL_USER')
    MAIL_PASSWORD = config('EMAIL_PASS')
    #SQLALCHEMY_ECHO = True
