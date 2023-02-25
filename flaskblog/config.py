import os

class Config:
    SECRET_KEY = 'ccac9e8fe240a1628b5aa81bd85549c4'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@10.103.7.2:5432/postgres-blog' 
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
