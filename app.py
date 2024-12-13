
from flask import Flask
from flask_babel import Babel

app = Flask(__name__)
app.config.from_object('config.Config')

babel = Babel(app)

@babel.localeselector
def get_locale():
    # Get the default locale from the configuration
    return app.config.get('BABEL_DEFAULT_LOCALE', 'fi')

# ...existing code...

if __name__ == '__main__':
    app.run()