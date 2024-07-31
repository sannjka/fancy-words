from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from config import config
import keras


bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
mail = Mail()
moment = Moment()

nn_model = keras.saving.load_model('app/paint/nn/model.keras')
nn_model_class = keras.saving.load_model('app/paint/nn/model_class.keras')
nn_model_0 = keras.saving.load_model('app/paint/nn/model_0.keras') # bezier
nn_model_1 = keras.saving.load_model('app/paint/nn/model_1.keras') # triangle
nn_model_2 = keras.saving.load_model('app/paint/nn/model_2.keras') # rectangle
nn_model_3 = keras.saving.load_model('app/paint/nn/model_3.keras') # ellipse

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    moment.init_app(app)

    # attach Blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .profile import profile as profile_blueprint
    app.register_blueprint(profile_blueprint)

    from .paint import paint as paint_blueprint
    app.register_blueprint(paint_blueprint)

    return app

