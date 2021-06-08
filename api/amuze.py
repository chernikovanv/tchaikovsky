import requests
import json
import time
from datetime import datetime 
import asyncio
import aiohttp

import logging
logger = logging.getLogger(__name__)

from mapper import ID_Mapper

id_mapper = ID_Mapper()

TOKEN = '89012be6a4b5099e3384360459355ac7'

AMUZE_GRAPHQL_API_URL = 'https://cdn.music.beeline.ru/api/v3/graphql'

QUERY_SHOWCASE = '''
query showcaseIds {
    showcase {
        blocks {
            dynamicContentIds: ids(type: dynamic_content) {
                totalCount
                pageInfo {
                    endCursor
                    hasNextPage
                }
                edges {
                    node {
                        id
                        signature
                    }
                }
            }
        }
    }
}
'''

QUERY_SHOWCASE_BLOCK = '''
query showcaseBlock($id: Int!, $first: Int = 20, $after: String) {
    showcase {
        blocks {
            block(id: $id) {
                id
                title
                description
                ... on showcaseBlockTracks {
                    tracks: content(first: $first, after: $after) {
                        totalCount
                        pageInfo {
                            endCursor
                            hasNextPage
                        }
                        edges {
                            node {
                                ...track
                            }
                        }
                    }
                }
                ... on showcaseBlockPlaylists {
                    playlists: content(first: $first, after: $after) {
                        edges {
                            node {
                                ...playlist
                            }
                        }
                    }
                }
                ... on showcaseBlockReleases {
                    releases: content(first: $first, after: $after) {
                        totalCount
                        pageInfo {
                            endCursor
                            hasNextPage
                        }
                        edges {
                            node {
                                ...release
                            }
                        }
                    }
                }
                ... on showcaseBlockArtists {
                    artists: content(first: $first, after: $after) {
                        totalCount
                        pageInfo {
                            endCursor
                            hasNextPage
                        }
                        edges {
                            node {
                                ...artist
                            }
                        }
                    }
                }
                ... on showcaseBlockUsers {
                    users: content(first: $first, after: $after) {
                        totalCount
                        pageInfo {
                            endCursor
                            hasNextPage
                        }
                        edges {
                            node {
                                ...user
                            }
                        }
                    }
                }
                ... on showcaseBlockClips {
                    clips: content(first: $first, after: $after) {
                        totalCount
                        pageInfo {
                            endCursor
                            hasNextPage
                        }
                        edges {
                            node {
                                ...clip
                            }
                        }
                    }
                }
            }
        }
    }
}

fragment track on Track {
    id
    title
    is_deleted
    is_available
    duration
    image(theme: black) {
        url
    }
    artist {
        id
        public_id
        title
        is_deleted
    }
    release {
        id
        public_id
        title
        date
    }
}

fragment playlist on Playlist {
    id
    title
    description
    image(theme: black) {
        url
    }
}

fragment release on Release {
    id
    title
    public_id
    is_deleted
    duration
    date
    image(theme: black) {
        url
    }
    artist {
        id
        title
        public_id
        imageBlack: image(theme: black) {
            url
        }
        imageWhite: image(theme: white) {
            url
        }
    }
}


fragment artist on Artist {
    id
    title
    image(theme: black) {
        url
    }
}


fragment user on PublicProfile {
    id
    name
    phone
    is_subscribed
    blackAvatar: avatar(theme: black) {
        url
    }
    whiteAvatar: avatar(theme: white) {
        url
    }
}


fragment clip on Clip {
    id
    external_id
    title
    description
    url
    is_deleted
    thumbnail_big: thumbnail(size: big)
    thumbnail_medium: thumbnail(size: medium)
    thumbnail_small: thumbnail(size: small)
}
'''

QUERY_PLAYLIST = '''
query playlist($id: Int!) {
    music {
        playlists(ids: [$id]) {
          id
          title
          description
          image(theme: black) {
              url
          }
          items {
            totalCount
            edges {
                node {
                    id
                    track_title
                    artist_title
                    duration
                    track {
                        ...track
                    }
                }
            }
        }
    }
  }
}

fragment track on Track {
    id
    title
    duration
    image(theme: black) {
        url
    }
    artist {
        id
        public_id
        title
    }
    release {
        id
        public_id
        title
        date
    }
}
'''

QUERY_PLAYLIST_WITH_STREAM_URL = '''
query playlist($id: Int!) {
    music {
        playlists(ids: [$id]) {
          id
          title
          description
          image(theme: black) {
              url
          }
          items {
            totalCount
            edges {
                node {
                    id
                    track_title
                    artist_title
                    duration
                    track {
                        ...track
                    }
                }
            }
        }
    }
  }
}

fragment track on Track {
    id
    title
    duration
    image(theme: black) {
        url
    }
    stream {
        url
    }
    artist {
        id
        public_id
        title
    }
    release {
        id
        public_id
        title
        date
    }
}
'''

class Amuze():
    def __init__(self):
        self.headers = {'token': TOKEN}

    def player_conversion(self, player):
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

        items = []

        for item in player['items']['edges']:
            id = id_mapper.ext2int('track', item['node']['id'])
            artist_id = id_mapper.ext2int('artist', item['node']['track']['artist']['id'])
            items.append({'id': id,
                          'track_type': 'audio',
                          'content_type': 'music',
                          'title': item['node']['track']['title'],
                          'images': [{'url': item['node']['track']['image']['url'],'size': 'thumbnail'}],
                          'authors': [{'id': artist_id, 'title': item['node']['track']['artist']['title']}],
                          'duration_ms': item['node']['track']['duration'] * 1000,
                          'progress_ms': 0,
                          'source_id' : None,
                          'context_title' : None,
                          'release_date': item['node']['track']['release']['date'],
                          'files' : [{'bitrate':128000,'codec':'codec','file_id':id}]
                          })

        player_state['tracks'] = items

        return player_state

    def playlist_conversion(self, playlist):
        playlist['id'] = id_mapper.ext2int('playlist', playlist['id'])
        playlist['images']: [{'url': playlist['image']['url'], 'size': 'thumbnail'}]
        playlist.pop('image')
        playlist['kind'] = 'playlist'

        items = []

        for item in playlist['items']['edges']:
            id = id_mapper.ext2int('track', item['node']['id'])
            artist_id = id_mapper.ext2int('artist', item['node']['track']['artist']['id'])
            items.append({'id': id,
                          'kind': 'track',
                          'title': item['node']['track']['title'],
                          'description': None,
                          'images': [{'url': item['node']['track']['image']['url'],'size': 'thumbnail'}],
                          'context': {'release_date' : item['node']['track']['release']['date'],
                                      'authors' : [{'id': artist_id, 'title': item['node']['track']['artist']['title']}],
                                      'duration_ms': item['node']['track']['duration']*1000,
                                      'description': None,
                                      'color': None,
                                      'icon_url': None,
                                      'id': None,
                                      'link': None,
                                      'track_count': None,
                                      'popular': None
                                      }
                          })

            playlist['items'] = items

            return playlist

    def blocks_conversion(self, blocks):
        for ind, item in enumerate(blocks):
            item['kind'] = 'list'
            item['title'] = {'text': item['title'],
                             'size': 'standard',
                             'highlight': None,
                             'action': None
                            }
            item['description'] = item['description']
            item['images'] = []
            item['items'] = []
            item['id'] = id_mapper.ext2int('block', item['id'])
            
            item_keys = item.keys()
            
            if 'playlists' in item_keys: 
                block_items_key = 'playlists'
                block_items_kind = 'playlist'
                for block_item in item[block_items_key]['edges']:
                    id = id_mapper.ext2int( block_items_kind, block_item['node']['id'])
                    item['items'].append({'id': id,
                                          'kind': block_items_kind,
                                          'title':block_item['node']['title'],
                                          'description':block_item['node']['description'],
                                          'images':[{'url':block_item['node']['image']['url'],
                                                     'size':'thumbnail'}],
                                          'context' : None
                                         })
                
            if 'tracks' in item_keys: 
                block_items_key = 'tracks'
                block_items_kind = 'track'
                for block_item in item[block_items_key]['edges']:
                    id = id_mapper.ext2int(block_items_kind, block_item['node']['id'])
                    item['items'].append({'id': id,
                                          'kind': block_items_kind,
                                           'title':block_item['node']['title'],
                                           'description':None,
                                           'images':[{'url':block_item['node']['image']['url'],
                                                      'size':'thumbnail'}],
                                           'context' : None
                                         })
                
            if 'artists' in item_keys: 
                block_items_key = 'artists'
                block_items_kind = 'artist'
                for block_item in item[block_items_key]['edges']:
                    id = id_mapper.ext2int(block_items_kind, block_item['node']['id'])
                    item['items'].append({'id': id,
                                          'kind': block_items_kind,
                                           'title':block_item['node']['title'],
                                           'description':None,
                                           'images':[{'url':block_item['node']['image']['url'],
                                                      'size':'thumbnail'}],
                                           'context' : None
                                         })
                
            if 'releases' in item_keys: 
                block_items_key = 'releases'
                block_items_kind = 'release'    
                for block_item in item[block_items_key]['edges']:
                    id = id_mapper.ext2int(block_items_kind, block_item['node']['id'])
                    item['items'].append({'id': id,
                                          'kind': block_items_kind, 
                                           'title':block_item['node']['title'],
                                           'description':None,
                                           'images':[{'url':block_item['node']['image']['url'],
                                                      'size':'thumbnail'}],
                                           'context' : None
                                         })

            item.pop(block_items_key)
            
        return blocks

    async def request(self, URL, json, headers):
        #id = json["variables"]["id"]
        #print(str(id) + ', start : ' + str(datetime.now()))
        async with aiohttp.ClientSession() as session:
            async with session.post(URL, json=json, headers=headers) as response:
                res = await response.json()
        #print(str(id) + ', end : ' + str(datetime.now()))
        return [response.status, res]

    def feed(self):
        start_time = datetime.now() 
        
        params = {"query":QUERY_SHOWCASE,"variables":{}}
        r = requests.post(AMUZE_GRAPHQL_API_URL, json=params, headers=self.headers)

        time_elapsed = datetime.now() - start_time
        #print('QUERY_SHOWCASE' + ', time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))
        logger.error('QUERY_SHOWCASE' + ', time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))
        
        if r.status_code != 200: return None
        
        items = r.json()['data']['showcase']['blocks']['dynamicContentIds']['edges']

        asyncio.set_event_loop(asyncio.new_event_loop())

        start_time = datetime.now()
        tasks = [self.request(AMUZE_GRAPHQL_API_URL, {"query":QUERY_SHOWCASE_BLOCK,"variables":{"id":item['node']['id']}}, self.headers) for item in items]
        res, _ = asyncio.run(asyncio.wait(tasks))
        time_elapsed = datetime.now() - start_time
        logger.error('QUERY_SHOWCASE_BLOCK ASYNC' + ', time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))

        blocks = [item.result()[1]['data']['showcase']['blocks']['block'] for item in res if item.result()[0] == 200]

        return {"timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
               "blocks":self.blocks_conversion(blocks)}

        # sequential requests
        blocks = []
        for item in items:
            id =item['node']['id']
            params = {"query":QUERY_SHOWCASE_BLOCK,"variables":{"id":id}}
            
            start_time = datetime.now()

            r = requests.post(AMUZE_GRAPHQL_API_URL, json=params, headers=self.headers)
        
            time_elapsed = datetime.now() - start_time
            #print('QUERY_SHOWCASE_BLOCK ' + str(id) + ', time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))
            logger.error('QUERY_SHOWCASE_BLOCK' + ', time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))
                
            if r.status_code == 200: 
                blocks.append(r.json()['data']['showcase']['blocks']['block'])
            
            #break

        return {"timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
               "blocks":self.blocks_conversion(blocks)}

    def feed_by_id(self, id):

        (ext_type, ext_id) = id_mapper.int2ext(id)

        if ext_type == 'playlist':
            start_time = datetime.now()

            params = {"query": QUERY_PLAYLIST, "variables": {'id':ext_id}}
            r = requests.post(AMUZE_GRAPHQL_API_URL, json=params, headers=self.headers)

            time_elapsed = datetime.now() - start_time
            # print('QUERY_SHOWCASE' + ', time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))
            logger.error('QUERY_PLAYLIST' + ', time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))

            if r.status_code != 200:
                logger.error(r.text)
                return None

            playlist = self.playlist_conversion(r.json()['data']['music']['playlists'][0])

            res = {"timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
                   "blocks": playlist}
        else:
            res = {'ext_type':ext_type, 'ext_id':ext_id}

        return res

    def player(self):
        params = {"query": QUERY_PLAYLIST_WITH_STREAM_URL, "variables": {'id': 56044}}
        r = requests.post(AMUZE_GRAPHQL_API_URL, json=params, headers=self.headers)
        player_state = self.player_conversion(r.json()['data']['music']['playlists'][0])
        return player_state
