from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    about_me = StringField('About me', validators=[DataRequired()])
    img = FileField('Profile picture', validators=[FileAllowed(['jpg','png','img'], 'Images only!')])
    submit = SubmitField('Submit')    
