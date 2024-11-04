from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError
from flask_wtf.file import FileAllowed
from app.models import User
from flask_login import current_user


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
    file = FileField('Profile picture', validators=[FileAllowed(['jpg','png','img'], 'Images only!')])
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


