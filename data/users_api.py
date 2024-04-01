import flask

import datetime
from werkzeug.security import generate_password_hash

from . import db_session
from .users import User

blueprint = flask.Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)

user_params = (
    'id',
    'surname',
    'name',
    'age',
    'position',
    'speciality',
    'address',
    'city_from',
    'email',
    'hashed_password',
    'modified_date',
)


@blueprint.route('/api/users', methods=['GET'])
def get_users():
    global user_params
    session = db_session.create_session()
    users = session.query(User).all()
    return flask.jsonify(
        {
            'users':
                [item.to_dict(only=user_params) for item in users]
        }
    )


@blueprint.route('/api/users/<int:user_id>', methods=['GET'])
def get_one_user(user_id):
    global user_params
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        return flask.make_response(flask.jsonify({'error': 'Not found'}), 404)
    return flask.jsonify(
        {
            'user': user.to_dict(only=user_params)
        }
    )


@blueprint.route('/api/users', methods=['POST'])
def create_users():
    if not flask.request.json:
        return flask.make_response(flask.jsonify({'error': 'Empty request'}), 400)
    elif (not all(key in flask.request.json for key in
                  ['email', 'password', 'surname', 'name', 'age', 'position', 'speciality', 'address'])
          or len(flask.request.json) != 8):
        return flask.make_response(flask.jsonify({'error': 'Bad request'}), 400)
    elif not isinstance(flask.request.json['age'], int):
        return flask.make_response(flask.jsonify({'error': 'Bad params'}), 400)
    session = db_session.create_session()
    user = User(
        email=str(flask.request.json['email']),
        surname=str(flask.request.json['surname']),
        name=str(flask.request.json['name']),
        age=int(flask.request.json['age']),
        position=str(flask.request.json['position']),
        speciality=str(flask.request.json['speciality']),
        address=str(flask.request.json['address']),
    )
    user.set_password(str(flask.request.json['password']))
    session.add(user)
    session.commit()
    return flask.jsonify({'id': user.id})


@blueprint.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        return flask.make_response(flask.jsonify({'error': 'Not found'}), 404)
    session.delete(user)
    session.commit()
    return flask.jsonify({'success': 'OK'})


@blueprint.route('/api/users/<int:user_id>', methods=['PUT'])
def edit_user(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        return flask.make_response(flask.jsonify({'error': 'Not found'}), 404)
    if len(flask.request.json.keys()) == 0:
        return flask.make_response(flask.jsonify({'error': 'No params'}), 400)
    if 'surname' in flask.request.json.keys():
        user.surname = str(flask.request.json['surname'])
    if 'name' in flask.request.json.keys():
        user.name = str(flask.request.json['name'])
    if 'age' in flask.request.json.keys():
        user.age = int(flask.request.json['age'])
    if 'position' in flask.request.json.keys():
        user.position = str(flask.request.json['position'])
    if 'speciality' in flask.request.json.keys():
        user.speciality = str(flask.request.json['speciality'])
    if 'address' in flask.request.json.keys():
        user.address = str(flask.request.json['address'])
    if 'city_from' in flask.request.json.keys():
        user.city_from = str(flask.request.json['city_from'])
    if 'password' in flask.request.json.keys():
        user.hashed_password = generate_password_hash(str(flask.request.json['password']))
    user.modified_date = datetime.datetime.now
    session.commit()
    return flask.jsonify({'success': 'OK'})
