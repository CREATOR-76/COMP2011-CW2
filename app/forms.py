from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SearchField
from wtforms.validators import DataRequired, Email, Length, EqualTo

# Login form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='The email address cannot be empty'),
        Email(message='The email is not valid')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='The password cannot be empty')
    ])
    submit = SubmitField('Login')

# Register Form
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message='The username cannot be empty'),
        Length(min=2, max=20, message='Username must be between 2 and 20 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email can not be empty'),
        Email(message='the e-mail is invalid')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='passport can not be empty'),
        Length(min=6, message='at least 6 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='The password must match')
    ])
    submit = SubmitField('Register')

# Search Form
class SearchForm(FlaskForm):
    query = StringField('Search', validators=[
        DataRequired(message='Please enter content')
    ])
    submit = SubmitField('Search')