import requests
from datetime import datetime
import uuid

import logging
logger = logging.getLogger(__name__)

from mapper import ID_Mapper

id_mapper = ID_Mapper()

TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOjEyNDY5NCwiaXNzIjoiaHR0cHM6Ly9hZG1pbi5iaWJsaW92ay5ydS9hcGkvdjEvYXV0aCIsImlhdCI6MTYyMzgzNjMzMywiZXhwIjoxNjI2NDI4MzMzLCJuYmYiOjE2MjM4MzYzMzMsImp0aSI6ImVxczhGM2pPWXQyRVJRVzkifQ.-pbGGvtAt2sobHlY8k06GLt_0rKSiltpcBpUeM9qp68'
BIBLIO_API_URL = 'https://admin.bibliovk.ru/api/v1'
EXT_PLATFORM = 'biblio'

class Biblio():
    def __init__(self):
        self.headers = {'Authorization': 'Bearer '+TOKEN,
                        'X-Client-Biblio-Lang': 'ru',
                        'X-Client-Biblio': 'andr-klDwcsnB1nmuyDCu9R-1.0',
                        'accept': 'application\json'
                        }

    def data_conversion(self, data):
        items = []
        for ind, item in enumerate(data):
            id = id_mapper.ext2int('book', item['id'],EXT_PLATFORM)
            items.append({'id': id,
                          'kind': 'book',
                          'title': item['title'],
                          'description': None,#item['bio'],
                          'images': [{'url': item['cover'],
                                      'size': 'thumbnail'}],
                          'context': {
                              'release_date': item['publish_date'][0:10],
                              "authors": [
                                  {
                                      "id": id_mapper.ext2int('author', item['author_id'],EXT_PLATFORM),
                                      "title": item['author_name']
                                  }
                              ],
                              "duration_ms": item['duration'],
                              "description": None,
                              "color": None,
                              "icon_url": None,
                              "id": None,
                              "link": None,
                              "track_count": item['tracks_count'],
                              "popular": None,
                              "stream_url": None,
                              "play_now": None
                          }
                         })

        return items

    def feed(self):
        start_time = datetime.now()

        params = {}
        r = requests.get(BIBLIO_API_URL+'/books/recomends', json=params, headers=self.headers)

        time_elapsed = datetime.now() - start_time
        logger.error('QUERY_BOOKS' + ', time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))

        if r.status_code != 200: return None

        block = {
            "id": str(uuid.uuid1()),
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
          "id": "4ed80719-30c2-46fb-863d-1995f0c3dd74",
          "kind": "book",
          "title": "1984",
          "description": "Своеобразный антипод второй великой антиутопии XX века – «О дивный новый мир» Олдоса Хаксли. Что, в сущности, страшнее: доведенное до абсурда «общество потребления» – или доведенное до абсолюта «общество идеи»? По Оруэллу, нет и не может быть ничего ужаснее тотальной несвободы…",
          "images": [
            {
              "url": "https://content.chk.dev.kode-t.ru/Books/Book-009/1/b2ff7e94-0193-4095-99db-08cec2c90bcb.png",
              "size": "thumbnail"
            }
          ],
          "context": {
            "release_date": "1949-01-01",
            "authors": [
              {
                "id": "fb546769-4213-46cf-9831-a5b1f69f6236",
                "title": "Джордж Оруэлл"
              }
            ],
            "duration_ms": 56832000,
            "description": None,
            "color": None,
            "icon_url": None,
            "id": None,
            "link": None,
            "track_count": 24,
            "popular": None,
            "stream_url": None,
            "play_now": None
          }
        }
      ]
        }

        block['items'] = self.data_conversion(r.json()['data'])

        return {"timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
                "blocks": [block]}
