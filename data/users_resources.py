from flask import jsonify
from flask_restful import abort, Resource

from . import db_session
from .users import User
from .users_parser import parser


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


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict(
            only=user_params)})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=user_params) for item in users]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            email=str(args['email']),
            surname=str(args['surname']),
            name=str(args['name']),
            age=int(args['age']),
            city_from=str(args['city_from']),
            position=str(args['position']),
            speciality=str(args['speciality']),
            address=str(args['address']),
        )
        user.set_password(args['password'])
        session.add(user)
        session.commit()
        return jsonify({'id': user.id})
