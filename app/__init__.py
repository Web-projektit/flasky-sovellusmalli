from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
from flask_login import LoginManager
from config import config
from flask_wtf import CSRFProtect
import logging
import sys

csrf = CSRFProtect()
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
# db = SQLAlchemy()
db = SQLAlchemy(session_options={"autoflush": False})
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

# Luo loggeri
logger = logging.getLogger('flask_app')
logger.setLevel(logging.DEBUG)
# Luo stdout handler
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
# Lisää formatteri handleriin
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stdout_handler.setFormatter(formatter)
# Lisää handler loggeriin
logger.addHandler(stdout_handler)
# Varmista, ettei duplikaatteja tule (jos loggeria kutsutaan uudelleen)
logger.propagate = False


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    # db.init_app(app)
    try:
        db.init_app(app)
    except OperationalError as e:
        app.logger.error(f"VIRHE: Database connection failed: {e}")
        # Handle the error, e.g., show a user-friendly message or retry connection
        return None

    csrf.init_app(app)
    
    login_manager.init_app(app)
    # Set Moment.js locale to Finnish
    # @app.context_processor
    # def inject_moment_locale():
    #    return {'moment_locale': 'fi'}


    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
