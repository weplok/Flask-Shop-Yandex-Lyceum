from flask import jsonify
from flask_restful import abort, Resource

from . import db_session
from .jobs import Jobs
from .jobs_parser import parser


jobs_params = (
    'id',
    'team_leader',
    'user.name',
    'user.surname',
    'job',
    'work_size',
    'collaborators',
    'start_date',
    'end_date',
    'is_finished',
)


def abort_if_jobs_not_found(jobs_id):
    session = db_session.create_session()
    jobs = session.query(Jobs).get(jobs_id)
    if not jobs:
        abort(404, message=f"Jobs {jobs_id} not found")


class JobsResource(Resource):
    def get(self, jobs_id):
        abort_if_jobs_not_found(jobs_id)
        session = db_session.create_session()
        jobs = session.query(Jobs).get(jobs_id)
        return jsonify({'jobs': jobs.to_dict(
            only=jobs_params)})

    def delete(self, jobs_id):
        abort_if_jobs_not_found(jobs_id)
        session = db_session.create_session()
        jobs = session.query(Jobs).get(jobs_id)
        session.delete(jobs)
        session.commit()
        return jsonify({'success': 'OK'})


class JobsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        jobs = session.query(Jobs).all()
        return jsonify({'jobs': [item.to_dict(
            only=jobs_params) for item in jobs]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        jobs = Jobs(
            team_leader=int(args['team_leader']),
            job=str(args['job']),
            work_size=int(args['work_size']),
            collaborators=str(args['collaborators']),
            is_finished=bool(args['is_finished']),
        )
        session.add(jobs)
        session.commit()
        return jsonify({'id': jobs.id})
