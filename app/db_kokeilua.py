from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/db_name'
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

# I: Lisää käyttäjiä tietokantaan tarkistamalla ensin, ettei käyttäjätunnuksia ole jo olemassa
def add_users(users):
    try:
        # Check for existing usernames in the database
        existing_usernames = {u.username for u in db.session.query(User).filter(User.username.in_([u['username'] for u in users])).all()}
        
        # Filter out users who already exist
        new_users = [User(username=user['username'], email=user['email']) for user in users if user['username'] not in existing_usernames]
        
        # Bulk save new users in a single transaction
        db.session.bulk_save_objects(new_users)
        db.session.commit()
        print("Users added successfully!")
    except IntegrityError:
        db.session.rollback()
        print("Duplicate users detected. Transaction rolled back.")
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred: {e}")

# Esimerkki käyttäjistä
users_to_add = [
    {"username": "user1", "email": "user1@example.com"},
    {"username": "user2", "email": "user2@example.com"},
    {"username": "user3", "email": "user3@example.com"}
]

# Käytä funktiota lisäämään käyttäjiä
add_users(users_to_add)


# II: Lisää käyttäjiä tietokantaan tarkistamatta ensin, ettei käyttäjätunnuksia ole jo olemassa
def add_users_without_checking(users):
    try:
        # Luo User-objektit ja lisää ne sessioniin
        new_users = [User(username=user['username'], email=user['email']) for user in users]
        db.session.bulk_save_objects(new_users)
        db.session.commit()
        print("Users added successfully!")
    except IntegrityError:
        db.session.rollback()
        print("Duplicate users detected. Transaction rolled back.")
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred: {e}")


# III: Lisää käyttäjiä tietokantaan käyttäen add-metodia
def add_users_with_add(users):
    try:
        # Lisää käyttäjät yksi kerrallaan sessioon
        for user_data in users:
            user = User(username=user_data['username'], email=user_data['email'])
            db.session.add(user)
        
        # Commitoi kaikki lisäykset yhdellä kertaa
        db.session.commit()
        print("Users added successfully!")
    except IntegrityError:
        db.session.rollback()
        print("Duplicate users detected. Transaction rolled back.")
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred: {e}")

# Esimerkkikäyttäjät
users_to_add = [
    {"username": "user1", "email": "user1@example.com"},
    {"username": "user2", "email": "user2@example.com"},
    {"username": "user3", "email": "user3@example.com"}
]

add_users_with_add(users_to_add)

#IV: Käyttäen SQL-kyselyä raakana lisäämään käyttäjiä
def add_users_with_native_sql():
    users = request.form.getlist('users')
    if len(users) > 0:
        query_start = "INSERT INTO users (id,active) VALUES "
        query_end = " ON DUPLICATE KEY UPDATE active = VALUES(active)"
        query_values = ""
        active = request.form.getlist('active')
        for v in users:
            if v in active:
                query_values += "("+v+",1),"
            else:
                query_values += "("+v+",0),"
        query_values = query_values[:-1]
        query = query_start + query_values + query_end
        # result = db.session.execute('SELECT * FROM my_table WHERE my_column = :val', {'val': 5})
        try:
            db.session.execute(query)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"An error occurred: {e}")
