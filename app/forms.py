from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SearchField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='Email不能为空'),
        Email(message='请输入有效的email地址')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='密码不能为空')
    ])
    submit = SubmitField('登录')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message='用户名不能为空'),
        Length(min=2, max=20, message='用户名长度必须在2-20之间')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email不能为空'),
        Email(message='请输入有效的email地址')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='密码不能为空'),
        Length(min=6, message='密码至少需要6个字符')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='请确认密码'),
        EqualTo('password', message='两次密码输入不一致')
    ])
    submit = SubmitField('注册')

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[
        DataRequired(message='请输入搜索内容')
    ])
    submit = SubmitField('搜索')