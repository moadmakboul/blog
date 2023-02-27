import os
import urllib.parse 
from dotenv import load_dotenv

load_dotenv()

params = urllib.parse.quote_plus(str(os.environ.get('connection_string')))


class Config:
    SECRET_KEY = 'ccac9e8fe240a1628b5aa81bd85549c4'
    SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc:///?odbc_connect={params}" 
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
