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


@blueprint.route('/api/jobs')
def get_jobs():
    global job_params
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    return flask.jsonify(
        {
            'jobs':
                [item.to_dict(only=job_params) for item in jobs]
        }
    )


@blueprint.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_one_job(job_id):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).get(job_id)
    if not job:
        return flask.make_response(flask.jsonify({'error': 'Not found'}), 404)
    return flask.jsonify(
        {
            'job': job.to_dict(only=job_params)
        }
    )
