from flask_wtf import FlaskForm
from wtforms import BooleanField, FileField, StringField, SubmitField, HiddenField, SelectField, DateTimeLocalField
from wtforms.validators import DataRequired, Length, Email, Regexp, Optional
from wtforms import ValidationError
from flask_wtf.file import FileAllowed
from app.models import User
from flask_login import current_user
from flask import current_app
from werkzeug.datastructures import FileStorage

app = current_app._get_current_object()
ALLOWED_EXTENSIONS = app.config['ALLOWED_EXTENSIONS']
 
def check_image_size(form, field):  
    MAX_FILE_SIZE = current_app.config.get('MAX_FILE_SIZE')  # 2 MB default
    file: FileStorage = field.data
    if file and file.content_length > MAX_FILE_SIZE:
        raise ValidationError(f"File size must be under {MAX_FILE_SIZE / (1024 * 1024)} MB.")

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), ])
    email = StringField('Email', validators=[DataRequired(), Length(5, 64), Email()])
    username = StringField('Username', validators=[ 
        DataRequired(), 
        Length(1, 64), 
        Regexp(r"^[a-zåäöA-ZÅÄÖ '_.\-]+$", 0, 'Usernames must have only letters, numbers, dots or underscores')
        ])
    location = StringField('Location', validators=[DataRequired()])
    about_me = StringField('About me', validators=[DataRequired()])
    file = FileField('Profile picture', validators=[FileAllowed(ALLOWED_EXTENSIONS, 'Images only!'),check_image_size])
    # HiddenField is used to store the name of the image file
    img = HiddenField("Img") 
    submit = SubmitField('Save profile')    

    def validate_email(self,field):
        new = field.data.lower()
        if current_user.email != new and User.query.filter_by(email=new).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        # Huom. MySQL on case-insensitive, joten vertailu on case-insensitive
        new = field.data
        if current_user.username != new and User.query.filter_by(username=new).first():
            raise ValidationError('Username already in use.')

    

class ProfileFormAdmin(FlaskForm):
    id = HiddenField('Id')
    name = StringField('Name', render_kw={'disabled': True})
    username = StringField('Username', render_kw={'disabled': True})
    email = StringField('Email', render_kw={'disabled': True})
    location = StringField('Location', render_kw={'disabled': True})
    about_me = StringField('About me', render_kw={'disabled': True})
    member_since = DateTimeLocalField('Member since', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    last_seen = DateTimeLocalField('Last seen', render_kw={'disabled': True})
    role_id = SelectField('Role', coerce=int, choices=[(1, 'User'), (2, 'Moderator'), (3, 'Administrator')])
    active = BooleanField('Active')
    submit = SubmitField('Save profile')    

    