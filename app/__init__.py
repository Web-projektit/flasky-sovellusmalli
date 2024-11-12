# Initialization and configuration of the Flask application
from flask import Flask,request,g
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
from flask_login import LoginManager
from config import config, get_datetime
from flask_wtf import CSRFProtect
import logging
import sys
from datetime import datetime
import pytz
from flask_babel import Babel
from flask_babel import _

class FinnishFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        helsinki_tz = pytz.timezone('Europe/Helsinki')
        created_time = datetime.fromtimestamp(record.created, tz=helsinki_tz)
        return created_time.strftime(datefmt or '%Y-%m-%d %H:%M:%S')

def get_locale():
    # Valitse kieli pyynnön perusteella tai selaimen kieliasetuksista
    selected_language = request.args.get('lang') or request.accept_languages.best_match(['fi', 'en'])
    print(f"Selected language: {selected_language}")  # Lisää tämä rivin tarkistamiseksi
    return selected_language

csrf = CSRFProtect()
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
babel = Babel()
# db = SQLAlchemy()
# with db.session.no_autoflush:, ei toimi, 
# joten se on korvattu alustuksella db = SQLAlchemy(session_options={"autoflush": False})    
# ks. fake.py 
db = SQLAlchemy(session_options={"autoflush": False})
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    # Configure the logger
    logger = app.logger  # Use Flask's built-in app logger
    # Remove any existing handlers
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)
    stderr_handler = logging.StreamHandler(sys.stderr)
    formatter = FinnishFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stderr_handler.setFormatter(formatter)
    logger.addHandler(stderr_handler)
    logger.propagate = False
    logger.info("Test log message with Helsinki time.")
    
    config[config_name].init_app(app)  # Call init_app after logger configuration
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
    babel.init_app(app, locale_selector=get_locale)
    print("INIT HELLO: "+ _("Hello"))
 
   # Set Moment.js locale to Finnish
    # @app.context_processor
    # def inject_moment_locale():
    #    return {'moment_locale': 'fi'}
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app

