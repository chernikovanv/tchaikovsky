import os
from flask import Flask, url_for, request
from datetime import datetime

from amuze import Amuze

# fix to avoid this error - https://github.com/jarus/flask-testing/issues/143 
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property

# monkey patch - https://stackoverflow.com/questions/67496857/cannot-import-name-endpoint-from-view-func-from-flask-helpers-in-python
import flask.scaffold
flask.helpers._endpoint_from_view_func = flask.scaffold._endpoint_from_view_func

from flask_restplus import Resource, Api
from flask_restplus import reqparse

# fix to run swagger behind  revers proxy
class Custom_API(Api):
    @property
    def specs_url(self):
        '''
        The Swagger specifications absolute url (ie. `swagger.json`)

        :rtype: str
        '''
        return url_for(self.endpoint('specs'), _external=False)

app = Flask(__name__)
api = Custom_API(app)

amz = Amuze()

ns = api.namespace('Сервис контента', path='/')

args = reqparse.RequestParser()
args.add_argument('id', type=str, required=False, default=None, help='uuid')
args.add_argument(
    'category',
    type=str,
    required=False,
    default=None,
    choices=['main'],
    help='category'
)
@ns.route('/feed/v1')
@ns.expect(args)
class feed(Resource):

    def get(self):

        req_args = args.parse_args(request)
        id = req_args.get('id', None)

        if id is not None:
            res = amz.feed_by_id(id)
        else:
            res = amz.feed()

        return res

    def head(self):
        return ('',204,{'Last-Modified': datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z")})

@ns.route('/story/v1')
class story(Resource):
    def get(self):
        return {'stories':[]}

ns_users = api.namespace('Сервис пользователей', path='/')

args = reqparse.RequestParser()
args.add_argument(
    'action',
    type=str,
    required=False,
    default=None,
    choices=['initialize'],
    help='action'
)
@ns_users.route('/player/v1')
@ns_users.expect(args)
class player(Resource):
    def post(self):
        player_state = {
            "tracks": [],
            "prev_tracks": [],
            "options": {
                "repeat_enabled": False,
                "shuffle_enabled": False
            },
            "state": {
                "is_playing": False
            }
        }
        return amz.player()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT'))
