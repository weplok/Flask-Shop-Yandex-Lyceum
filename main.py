import flask
from flask import Flask, abort, redirect, render_template, request
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from flask_restful import Api
import data.db_session as db_session

import data.jobs_api as jobs_api
import data.users_api as users_api
import data.errors_handler as errors_handler

import data.users_resources as users_resources
import data.jobs_resources as jobs_resources

from data.users import User
from data.jobs import Jobs
from forms.user import LoginForm, RegisterForm
from forms.jobs import AddJobForm, EditJobForm

import dotenv
import os
import requests

dotenv.load_dotenv()

app = Flask(import_name='localhost')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', default='flask_secret_key')
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def main():
    db_session.global_init("db/mars_explorer.db")

    app.register_blueprint(errors_handler.blueprint)
    app.register_blueprint(jobs_api.blueprint)
    app.register_blueprint(users_api.blueprint)

    api.add_resource(users_resources.UsersListResource, '/api/v2/users')
    api.add_resource(users_resources.UsersResource, '/api/v2/users/<int:user_id>')

    api.add_resource(jobs_resources.JobsListResource, '/api/v2/jobs')
    api.add_resource(jobs_resources.JobsResource, '/api/v2/jobs/<int:jobs_id>')

    app.run(port=5000)


@app.route('/')
def jobs():
    session = db_session.create_session()
    jobs_list = session.query(Jobs).all()
    return render_template('jobs.html', jobs=jobs_list)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/register")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user_params = {
            'surname': form.surname.data.capitalize(),
            'name': form.name.data.capitalize(),
            'age': form.age.data,
            'city_from': form.city_from.data,
            'position': form.position.data,
            'speciality': form.speciality.data,
            'address': form.address.data,
            'email': form.email.data,
            'password': form.password.data
        }
        requests.post('http://localhost:5000/api/v2/users', json=user_params)
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/addjob', methods=['GET', 'POST'])
@login_required
def addjob():
    form = AddJobForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        job = Jobs(
            team_leader=form.team_leader.data,
            job=form.job.data,
            work_size=form.work_size.data,
            collaborators=form.collaborators.data,
            is_finished=form.is_finished.data,
        )
        session.add(job)
        session.commit()
        return redirect('/')
    return render_template('addjob.html', title='Работа', form=form)


@app.route('/editjob/<int:job_id>/<int:user_id>', methods=['GET', 'POST'])
@login_required
def editjob(job_id, user_id):
    form = EditJobForm()
    if request.method == "GET":
        session = db_session.create_session()
        job = session.query(Jobs).filter(Jobs.id == job_id).first()
        if ((user_id == job.team_leader or user_id == 1)
                and current_user.id == user_id):
            form.job.data = job.job
            form.work_size.data = job.work_size
            form.collaborators.data = job.collaborators
            form.is_finished.data = job.is_finished
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        job = session.query(Jobs).filter(Jobs.id == job_id).first()
        if job:
            job.job = form.job.data
            job.work_size = form.work_size.data
            job.collaborators = form.collaborators.data
            job.is_finished = form.is_finished.data
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('editjob.html', form=form)


@app.route('/deletejob/<int:job_id>/<int:user_id>', methods=['GET', 'POST'])
@login_required
def deletejob(job_id, user_id):
    session = db_session.create_session()
    job = session.query(Jobs).filter(Jobs.id == job_id).first()
    if ((user_id == job.team_leader or user_id == 1)
            and current_user.id == user_id):
        session.delete(job)
        session.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/users_show/<int:user_id>', methods=['GET'])
def users_show(user_id):
    # Объект пользователя
    user = requests.get(f'http://localhost:5000/api/users/{user_id}').json()
    if 'error' in user.keys():
        return flask.make_response(flask.jsonify({'error': 'Not found'}), 404)
    user = user['user']

    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = 'dda3ddba-c9ea-4ead-9010-f43fbc15c6e3'
    search_params = {
        "apikey": api_key,
        "text": user['city_from'],
        "lang": "ru_RU"
    }
    response = requests.get(search_api_server, params=search_params)
    if not response:
        return 'Город не найден :('

    # Преобразуем ответ в json-объект
    json_response = response.json()
    # Получаем первый найденный город.
    city = json_response["features"][0]
    # Получаем координаты ответа.
    point = city["geometry"]["coordinates"]
    org_point = "{0},{1}".format(point[0], point[1])
    delta = "0.05"
    # Собираем параметры для запроса к StaticMapsAPI:
    map_params = {
        # позиционируем карту центром на наш исходный адрес
        "spn": ",".join([delta, delta]),
        "l": "map",
        # добавим точку, чтобы указать найденный город
        "pt": "{0},pm2dgl".format(org_point)
    }

    map_api_server = "http://static-maps.yandex.ru/1.x/"
    # ... и выполняем запрос
    response = requests.get(map_api_server, params=map_params)
    return flask.render_template('users_show.html',
                                 name=user['name'],
                                 surname=user['surname'],
                                 city=user['city_from'],
                                 img=response.url)


if __name__ == '__main__':
    main()
