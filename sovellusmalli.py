import os
import click
from flask_migrate import Migrate
from app import create_app, db
from app.models import User, Role
import polib
import gettext
# from gettext import gettext as _

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)
# Tämä, jos tauluja eikä migraatiotiedostoja ole käytettävissä
# db.create_all()
# Tämä, jos Flask-komentorivi ei ole käytössä roolien lisäämiseen
# with app.app_context():
    # query = db.session.query(Role).first()
    # if not query:
        # print("query: "+str(query))
        # Role.insert_roles()

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


@app.cli.command()
@click.argument('test_names', nargs=-1)
def test(test_names):
    """Run the unit tests."""
    import unittest
    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

# Lataa .mo-tiedosto

'''
@app.context_processor
def inject_translations():
    return dict(_=gettext.gettext)
'''

fi_translations = gettext.translation('messages', localedir='translations', languages=['fi'])
fi_translations.install()
print("Python-käännös:"+ _("Hello"))


mo_path = 'translations/en/LC_MESSAGES/messages.mo'
mo = polib.mofile(mo_path)

# Tulosta kaikki käännökset
for entry in mo:
    print(f"Original: {entry.msgid}")
    print(f"Translated: {entry.msgstr}")
    print("Python-käännös: " + _("Hello"))