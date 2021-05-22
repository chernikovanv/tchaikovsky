import os
from flask import Flask, url_for, request
#from quart import Quart, url_for, request

from amuze import Amuze

# fix to avoid this error - https://github.com/jarus/flask-testing/issues/143 
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property

from flask_restplus import Resource, Api
from flask_restplus import reqparse

#from quart_restplus import Resource, Api
#from quart_restplus import reqparse

args = reqparse.RequestParser()
args.add_argument('id', type=str, required=False, default=None, help='uuid')

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
#app = Quart(__name__)
api = Custom_API(app)

amz = Amuze()

ns = api.namespace('Сервис контента', path='/')

@ns.route('/feed')
#@ns.param('id', 'uuid')
#@ns.doc(params={'id': 'uuid'})
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
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT'))
