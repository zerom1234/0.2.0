# app/db.py

from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager

mail = Mail()
loginManager = LoginManager()
db = SQLAlchemy()