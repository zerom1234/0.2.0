from flask import Flask
from config import config_by_name
from .db import db, mail, loginManager
from .routes import main as main_blueprint
from .functions import load_user


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    db.init_app(app)
    #for mail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USERNAME'] = 'erayrelationclient@gmail.com'
    app.config['MAIL_DEFAULT_SENDER'] = 'erayrelationclient@gmail.com'
    app.config['MAIL_PASSWORD'] = 'nzrlnazidocuflxv'
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    mail.init_app(app)
    loginManager.init_app(app)
    @loginManager.user_loader
    def user_loader(user_id):
        return load_user(user_id)
    loginManager.login_view = 'main.login'
    app.register_blueprint(main_blueprint)

    return app
