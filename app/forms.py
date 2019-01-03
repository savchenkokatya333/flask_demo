from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import TextAreaField
from wtforms.validators import ValidationError, DataRequired, EqualTo, Length
from app.models import User


class LoginForm(FlaskForm):
    userName = StringField('用户名:', validators=[DataRequired()])
    userPwd = PasswordField('密码:', validators=[DataRequired()])
    rememberMe = BooleanField('记住我')
    submit = SubmitField('登录')


class RegistrationForm(FlaskForm):
    userName = StringField('用户名', validators=[DataRequired()])
    phone = StringField('电话', validators=[DataRequired()])
    userPwd = PasswordField('密码', validators=[DataRequired()])
    userPwd2 = PasswordField('重复密码', validators=[DataRequired(), EqualTo('userPwd')])
    submit = SubmitField('注册')

    def validate_userName(self, userName):
        user = User.query.filter_by(userName=userName.data).first()
        if user is not None:
            raise ValidationError('用户名已存在')


class EditProfileForm(FlaskForm):
    userName = StringField('用户名', validators=[DataRequired()])
    about_me = TextAreaField('介绍...', validators=[Length(min=0, max=140)])
    submit = SubmitField('修改')


class PostForm(FlaskForm):
    post = TextAreaField('说点什么...', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('发表')
