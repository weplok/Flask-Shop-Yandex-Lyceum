from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, IntegerField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    surname = StringField('Фамилия колониста', validators=[DataRequired()])
    name = StringField('Имя kолониста', validators=[DataRequired()])
    age = IntegerField('Возраст колониста', validators=[DataRequired()])
    city_from = StringField('Родной город колониста', validators=[DataRequired()], default='Москва')
    position = StringField('Должность в команде', validators=[DataRequired()])
    speciality = StringField('Профессия', validators=[DataRequired()])
    address = StringField('Место жительства', validators=[DataRequired()])

    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')