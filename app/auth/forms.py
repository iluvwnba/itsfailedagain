__author__ = 'Martin'
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, length, regexp, equal_to
from ..models import User


class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired(), length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log in')

    # TODO Reg form regex
class RegisterForm(Form):
    username = StringField('Username', validators=[DataRequired(), regexp(), length(1, 64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired, length(1,64), equal_to('password2',
                                                                                          'Passwords dont match')])
    password2 = PasswordField('Password', validators=[DataRequired, length(1,64)])
    submit = SubmitField('Submit')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError