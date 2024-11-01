from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Email, Regexp
# from wtforms import ValidationError
from flask_wtf.file import FileAllowed


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
    img = FileField('Profile picture', validators=[FileAllowed(['jpg','png','img'], 'Images only!')])
    # img = HiddenField("img") 
    submit = SubmitField('Submit')    
