import random
from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import User


def users(count=100):
    fake_users = []
    fake = Faker(['fi_FI'])
    fake.unique.clear()
    i = 0
    while i < count:
        u = User(email=fake.unique.email(),
                 username=fake.unique.user_name(),
                 # username = 'tupla',
                 password='password',
                 confirmed=random.choice([True, False]),
                 # name=fake.name(),
                 # location=fake.city(),
                 # about_me=fake.text(),
                 # member_since=fake.past_date()
                 )
        # if u.username in [user.username for user in fake_users]:
        #    continue
        db.session.add(u)
        fake_users.append(u)
        print("fake_user: "+str(u))
        i += 1
    try:
        # Huom. tämä ei vielä riitä poistamaan virhettä
        # with db.session.no_autoflush:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        fake_users = []
        print("virhe: useita samoja käyttäjätunnuksia")
    print("fake_users: "+str(fake_users))
    return fake_users

