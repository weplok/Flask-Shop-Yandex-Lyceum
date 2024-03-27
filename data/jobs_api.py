import flask

from . import db_session
from .jobs import Jobs

blueprint = flask.Blueprint(
    'jobs_api',
    __name__,
    template_folder='templates'
)

job_params = (
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


@blueprint.route('/api/jobs', methods=['GET'])
def get_jobs():
    global job_params
    session = db_session.create_session()
    jobs = session.query(Jobs).all()
    return flask.jsonify(
        {
            'jobs':
                [item.to_dict(only=job_params) for item in jobs]
        }
    )


@blueprint.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_one_job(job_id):
    session = db_session.create_session()
    job = session.query(Jobs).get(job_id)
    if not job:
        return flask.make_response(flask.jsonify({'error': 'Not found'}), 404)
    return flask.jsonify(
        {
            'job': job.to_dict(only=job_params)
        }
    )


@blueprint.route('/api/jobs', methods=['POST'])
def create_jobs():
    if not flask.request.json:
        return flask.make_response(flask.jsonify({'error': 'Empty request'}), 400)
    elif not all(key in flask.request.json for key in
                 ['team_leader', 'job', 'work_size', 'collaborators', 'is_finished']) or len(flask.request.json) != 5:
        return flask.make_response(flask.jsonify({'error': 'Bad request'}), 400)
    elif (not isinstance(flask.request.json['team_leader'], int) or
          not isinstance(flask.request.json['work_size'], int) or
          not isinstance(flask.request.json['is_finished'], bool)):
        return flask.make_response(flask.jsonify({'error': 'Bad params'}), 400)
    session = db_session.create_session()
    jobs = Jobs(
        team_leader=int(flask.request.json['team_leader']),
        job=str(flask.request.json['job']),
        work_size=int(flask.request.json['work_size']),
        collaborators=str(flask.request.json['collaborators']),
        is_finished=bool(flask.request.json['is_finished']),
    )
    session.add(jobs)
    session.commit()
    return flask.jsonify({'id': jobs.id})


@blueprint.route('/api/jobs/<int:job_id>', methods=['DELETE'])
def delete_jobs(job_id):
    session = db_session.create_session()
    job = session.query(Jobs).get(job_id)
    if not job:
        return flask.make_response(flask.jsonify({'error': 'Not found'}), 404)
    session.delete(job)
    session.commit()
    return flask.jsonify({'success': 'OK'})
