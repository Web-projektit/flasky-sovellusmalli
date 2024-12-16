# Initialization and configuration of the Flask application
from flask import Flask,request,g,current_app,has_request_context,has_app_context
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
from flask_login import LoginManager
from config import config, get_datetime
from flask_wtf import CSRFProtect
from flask_cors import CORS
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
    # Huom. None-arvoa ei ole testattu
    selected_language = None
    if has_app_context():
        print("Has app context")
        # default = current_app.config['BABEL_DEFAULT_LOCALE']
        default = current_app.config.get('PREFERRED_LOCALE', 'fi')
        # Valitse kieli evästeen tai pyynnön perusteella tai selaimen kieliasetuksista
        if has_request_context():
            selected_language = request.cookies.get('lang') or request.args.get('lang') or request.accept_languages.best_match(['fi', 'en']) or default
        else:
            selected_language = default
    print(f"Selected language: {selected_language}")  # Lisää tämä rivin tarkistamiseksi
    g.lang = selected_language
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
'''Jos blueprintille tarvitaan oma unauthorized_handler, se
voidaan toteuttaa aiheuttamalla puuttuvalla login_view:llä
401-virhe ja käsitellä se blueprintin 401-virhekäsittelijällä.'''
login_manager.blueprint_login_views = {'reactapi':'','react':''}
''' Jos taas yksi login_manager ja sen unauthorized_handler riittävät,
tämä ei aiheuta 401-virhettä:
login_manager.unauthorized_handler(kirjautumisvirhe)'''


def create_app(config_name):
    app = Flask(__name__)
    # Huom. Tässä haetaan aluksi konfiguraatiotiedot
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
    
    bootstrap.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    CORS(app,
        supports_credentials=True,
        expose_headers=["Content-Type","X-CSRFToken"])

    # db.init_app(app)
    try:
        db.init_app(app)
    except OperationalError as e:
        app.logger.error(f"VIRHE: Database connection failed: {e}")
        # Handle the error, e.g., show a user-friendly message or retry connection
        return None
    # Huom. Tässä konfiguraatio on jo haettu, joten init_app voi käyttää sitä ja edeltävää
    # tietokanta-alustusta.
    config[config_name].init_app(app)  # Call init_app after logger configuration
    login_manager.init_app(app) 
    babel.init_app(app, locale_selector=get_locale)
    with app.app_context():
        """
        Huom. Tarvitaan app.app_context() alustetun Babelin käyttämiseen,
        kun request- tai g-oliot eivät ole käytettävissä. Muuten kutsuttaisiin
        Babelin _()-funktiota suoraan ilman alustusta.
        """
        print("INIT HELLO: "+ _("Hello"))
  
    # Set Moment.js locale to Finnish
    # @app.context_processor
    # def inject_moment_locale():
    #    return {'moment_locale': 'fi'}
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .reactapi import reactapi as reactapi_blueprint
    app.register_blueprint(reactapi_blueprint, url_prefix='/reactapi')

    return app

