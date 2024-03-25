import flask

from . import db_session
from .jobs import Jobs

blueprint = flask.Blueprint(
    'jobs_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/jobs')
def get_news():
    db_sess = db_session.create_session()
    news = db_sess.query(Jobs).all()
    return flask.jsonify(
        {
            'news':
                [item.to_dict(only=(
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
                ))
                    for item in news]
        }
    )
