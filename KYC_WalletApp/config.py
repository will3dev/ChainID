import os

class Config:
    SECRET_KEY = "KChofa1233!"
    SQLALCHEMY_DATABASE_URI = "sqlite:///site.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = "True"
    MAIL_SERVER = 'mail.privateemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'general@will3dev.com'
    MAIL_PASSWORD = "KChofa1233!"
    MAIL_DEFAULT_SENDER = 'general@will3dev.com'