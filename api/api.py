import os
from flask import Flask, url_for

# fix to avoid this error - https://github.com/jarus/flask-testing/issues/143 
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property

from flask_restplus import Resource, Api

class Custom_API(Api):
    @property
    def specs_url(self):
        '''
        The Swagger specifications absolute url (ie. `swagger.json`)

        :rtype: str
        '''
        return url_for(self.endpoint('specs'), _external=False)

app = Flask(__name__)                  #  Create a Flask WSGI application
api = Custom_API(app)                  #  Create a Flask-RESTPlus API

@api.route('/hello')                   #  Create a URL route to this resource
class HelloWorld(Resource):            #  Create a RESTful resource
    def get(self):                     #  Create GET endpoint
        return {'hello': 'world'}
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT'))
