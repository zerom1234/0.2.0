from ... import db
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(128), unique=True ,nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    activate = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(100), nullable=False)
    inscription_time = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __init__(self, username, email, password, activate, type):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.activate = activate
        self.type = type

    def check_passord(self, password):
        return check_password_hash(self.password_hash, password)
    
class Video(db.Model):
    __tablename__ = 'video'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    id_module = db.Column(db.Integer, nullable=False)
    original_namefile = db.Column(db.String(100), nullable=False)
    id_image_video = db.Column(db.String(100), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __init__(self, filename, id_module, original_namefile, id_image_video):
        self.filename = filename
        self.id_module = id_module
        self.original_namefile = original_namefile
        self.id_image_video = id_image_video

class image(db.Model):
    __tablename__ = 'Image'
    id = db.Column(db.Integer, primary_key=True)
    image_filename = db.Column(db.String(100), nullable=False)
    image_original_name = db.Column(db.String(100), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __init__(self, image_filename, image_original_name):
        self.image_filename = image_filename
        self.image_original_name = image_original_name

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False)
    image_id = db.Column(db.Integer, nullable=False)

    def __init__(self, category_name, image_id):
        self.category_name = category_name
        self.image_id = image_id

class module(db.Model):
    __tablename__ = 'module'
    id = db.Column(db.Integer, primary_key=True)
    name_module = db.Column(db.String(100), nullable=False)
    description_module = db.Column(db.Text, nullable=True)
    id_image_module = db.Column(db.Integer, nullable=False)
    id_category = db.Column(db.Integer, nullable=False)
    prix = db.Column(db.Integer, nullable=False)
    creation_time = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __init__(self, name_module, description_module, id_image_module, id_category, prix):
        self.name_module = name_module
        self.description_module = description_module
        self.id_image_module = id_image_module
        self.id_category = id_category
        self.prix = prix

class Video_buy(db.Model):
    __tablename__ = 'Video_buy'
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, nullable=False)
    id_module = db.Column(db.Integer, nullable=False)
    creation_time = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __init__(self, id_user, id_module):
        self.id_user = id_user
        self.id_module = id_module