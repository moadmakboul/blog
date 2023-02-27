import os
import urllib.parse 

params = urllib.parse.quote_plus("Driver={ODBC Driver 18 for SQL Server};Server=tcp:blog-flask.database.windows.net,1433;Database=flask-blog;Uid=moad;Pwd=postgres23*;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;")


class Config:
    SECRET_KEY = 'ccac9e8fe240a1628b5aa81bd85549c4'
    SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc:///?odbc_connect={params}" 
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
