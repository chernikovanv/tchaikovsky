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

        res['blocks'].append({
      "id": "83e4f670-6967-4c2a-a2c3-fcbe737250cb",
      "kind": "card_wide",
      "title": {
        "text": "Аудиокниги",
        "size": "large",
        "highlight": None,
        "action": None
      },
      "description": None,
      "images": [
        {
          "url": "https://content.chk.dev.kode-t.ru/images/blur%2Bfill.jpg",
          "size": "thumbnail"
        }
      ],
      "items": [
        {
          "id": "67459746-c1ff-4c5e-91b3-f677b6864c21",
          "kind": "book",
          "title": "Тонкое искусство пофигизма",
          "description": "Современное общество пропагандирует культ успеха: будь умнее, богаче, продуктивнее – будь лучше всех. Соцсети изобилуют историями на тему, как какой-то малец придумал приложение и заработал кучу денег, статьями в духе «Тысяча и один способ быть счастливым», а фото во френдленте создают впечатление, что окружающие живут лучше и интереснее, чем мы. Однако наша зацикленность на позитиве и успехе лишь напоминает о том, чего мы не достигли, о мечтах, которые не сбылись. Как же стать по-настоящему счастливым? Популярный блогер Марк Мэнсон в книге «Тонкое искусство пофигизма» предлагает свой, оригинальный подход к этому вопросу. Его жизненная философия проста – необходимо научиться искусству пофигизма. Определив то, до чего вам действительно есть дело, нужно уметь наплевать на все второстепенное, забить на трудности, послать к черту чужое мнение и быть готовым взглянуть в лицо неудачам и показать им средний палец.",
          "images": [
            {
              "url": "https://content.chk.dev.kode-t.ru/Books/Book-003/1/f8bdf5aa-b631-48e4-981e-0a6eb580f899.png",
              "size": "thumbnail"
            }
          ],
          "context": {
            "release_date": "2016-01-01",
            "authors": [
              {
                "id": "0d47c7f8-b50e-4e87-af3a-8eba014cd84f",
                "title": "Марк Мэнсон"
              }
            ],
            "duration_ms": 19013000,
            "description": None,
            "color": None,
            "icon_url": None,
            "id": None,
            "link": None,
            "track_count": 39,
            "popular": None,
            "stream_url": None,
            "play_now": False
          }
        }
      ]
    })

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
