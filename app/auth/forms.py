from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from flask_babel import lazy_gettext as _l
from ..models import User


class LoginForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Length(1, 64),
                                                 Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Keep me logged in'))
    submit = SubmitField(_l('Log In'))

# ^[a-zåäöA-ZÅÄÖ '_.\-]+$
class RegistrationForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Length(5, 64),
                                                 Email()])
    username = StringField(_l('Username'), validators=[
        DataRequired(), Length(1, 64),
        Regexp(r'^[a-zåäöA-ZÅÄÖ \'_.-]+$', 0,
               _l('Usernames must have only letters, numbers, dots or '
                  'underscores'))])
    password = PasswordField(_l('Password'), validators=[
        DataRequired(), EqualTo('password2', message=_l('Passwords must match.'))])
    password2 = PasswordField(_l('Confirm password'), validators=[DataRequired()])
    submit = SubmitField(_l('Register'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError(_l('Email already registered.'))

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(_l('Username already in use.'))


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(_l('Old password'), validators=[DataRequired()])
    password = PasswordField(_l('New password'), validators=[
        DataRequired(), EqualTo('password2', message=_l('Passwords must match.'))])
    password2 = PasswordField(_l('Confirm new password'),
                              validators=[DataRequired()])
    submit = SubmitField(_l('Update Password'))


class PasswordResetRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Length(1, 64),
                                                 Email()])
    submit = SubmitField(_l('Reset Password'))


class PasswordResetForm(FlaskForm):
    password = PasswordField(_l('New Password'), validators=[
        DataRequired(), EqualTo('password2', message=_l('Passwords must match'))])
    password2 = PasswordField(_l('Confirm password'), validators=[DataRequired()])
    submit = SubmitField(_l('Reset Password'))


class ChangeEmailForm(FlaskForm):
    email = StringField(_l('New Email'), validators=[DataRequired(), Length(1, 64),
                                                     Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    submit = SubmitField(_l('Update Email Address'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError(_l('Email already registered.'))
