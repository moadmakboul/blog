import os

class Config:
    SECRET_KEY = 'ccac9e8fe240a1628b5aa81bd85549c4'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///blog_data.db' 
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
