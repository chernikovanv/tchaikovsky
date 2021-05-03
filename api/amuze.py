import requests
import json
import time
from datetime import datetime 

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

class Amuze():
    def __init__(self):
        self.headers = {'token': TOKEN}
    
    def blocks_conversion(self, blocks):
        for ind, item in enumerate(blocks):
            item['kind'] = 'list'
            item['title'] = {'text': item['title'],
                             'size': 'standard',
                             'highlight': None,
                             'action': None
                            }
            item['description'] = None
            item['images'] = []
            item['items'] = []
            
            item_keys = item.keys()
            
            if 'playlists' in item_keys: 
                block_items_key = 'playlists'
                block_items_kind = 'playlist'
                for block_item in item[block_items_key]['edges']:
                    item['items'].append({'id':block_item['node']['id'],
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
                    item['items'].append({'id':block_item['node']['id'],
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
                    item['items'].append({'id':block_item['node']['id'],
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
                    item['items'].append({'id':block_item['node']['id'],
                                          'kind': block_items_kind, 
                                           'title':block_item['node']['title'],
                                           'description':None,
                                           'images':[{'url':block_item['node']['image']['url'],
                                                      'size':'thumbnail'}],
                                           'context' : None
                                         })

            item.pop(block_items_key)
            
        return blocks
        
    def feed(self):
        start_time = datetime.now() 
        
        params = {"query":QUERY_SHOWCASE,"variables":{}}
        r = requests.post(AMUZE_GRAPHQL_API_URL, json=params, headers=self.headers)
        
        time_elapsed = datetime.now() - start_time
        #print('QUERY_SHOWCASE' + ', time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))
    
        if r.status_code != 200: return None
        
        items = r.json()['data']['showcase']['blocks']['dynamicContentIds']['edges']
        
        blocks = []
        for item in items:
            id =item['node']['id']
            params = {"query":QUERY_SHOWCASE_BLOCK,"variables":{"id":id}}
            
            start_time = datetime.now() 
            
            r = requests.post(AMUZE_GRAPHQL_API_URL, json=params, headers=self.headers)
        
            time_elapsed = datetime.now() - start_time
            #print('QUERY_SHOWCASE_BLOCK ' + str(id) + ', time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))
            
            if r.status_code == 200: 
                blocks.append(r.json()['data']['showcase']['blocks']['block'])
            
            #break
        
        return {"timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
                "blocks":self.blocks_conversion(blocks)}
