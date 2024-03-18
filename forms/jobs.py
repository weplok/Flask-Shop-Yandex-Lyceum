from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, BooleanField
from wtforms.validators import DataRequired


class AddJobForm(FlaskForm):
    team_leader = IntegerField('id Руководителя работы', validators=[DataRequired()])
    job = StringField('Название работы', validators=[DataRequired()])
    work_size = IntegerField('Объём работ (в часах)', validators=[DataRequired()])
    collaborators = StringField('Задействованные лица (id через запятую с пробелом)')
    is_finished = BooleanField('Работа завершена? (Досрочное выполнение)', default=False)

    submit = SubmitField('Добавить работу')


class EditJobForm(FlaskForm):
    job = StringField('Название работы')
    work_size = IntegerField('Объём работ (в часах)')
    collaborators = StringField('Задействованные лица (id через запятую с пробелом)')
    is_finished = BooleanField('Работа завершена?', default=False)

    submit = SubmitField('Изменить данные работы')
