import uuid
import os

class ID_Mapper():
    def __init__(self, storage_type='memory'):
        
        self.storage_type = storage_type
        
        if self.storage_type == 'memory':
            self.map_ext2int = {}
            self.map_int2ext = {}
        
        if self.storage_type == 'db':
            from cassandra.cluster import Cluster
            DB_HOST = os.getenv('DB_HOST')
            self.cluster = Cluster([DB_HOST])
            self.session = self.cluster.connect()
            CQL = '''CREATE KEYSPACE IF NOT EXISTS id_mapping
                     WITH replication = {'class': 'SimpleStrategy', 'replication_factor' : 3};'''
            self.session.execute(CQL)
            self.session.set_keyspace('id_mapping')
            CQL = '''CREATE TABLE IF NOT EXISTS ext2int (
                    ext_source TEXT
                    , ext_type TEXT
                    , ext_id TEXT
                    , int_id UUID
                    , PRIMARY KEY ((ext_source, ext_type, ext_id), int_id)
                    )
                    '''
            self.session.execute(CQL)
            CQL = '''CREATE TABLE IF NOT EXISTS int2ext (
                    int_id UUID
                    , ext_source TEXT
                    , ext_type TEXT
                    , ext_id TEXT
                    , PRIMARY KEY (int_id, ext_source, ext_type, ext_id)
                    )
                    '''
            self.session.execute(CQL)

    def ext2int(self, ext_type, ext_id):
        
        if self.storage_type == 'db':
            CQL = "SELECT int_id FROM ext2int where ext_source='{}' and ext_type='{}' and ext_id='{}'"
            CQL = CQL.format('amuze',str(ext_type),str(ext_id))
            rows = self.session.execute(CQL)
            for row in rows:
                return str(row.int_id)
            return None    
            
        if self.storage_type == 'memory':
            if ext_type not in self.map_ext2int.keys(): self.map_ext2int[ext_type] = {}

            try:
                int_key = self.map_ext2int[ext_type][ext_id]
            except:
                int_key = str(uuid.uuid1())
                self.map_ext2int[ext_type][ext_id] = int_key
                self.map_int2ext[int_key] = (ext_type, ext_id)
            return int_key

    def int2ext(self, int_key):
        if self.storage_type == 'db':
            CQL = "SELECT ext_type,ext_id FROM int2ext where int_id={}"
            CQL = CQL.format(str(int_key))
            rows = self.session.execute(CQL)
            for row in rows:
                return (row.ext_type,row.ext_id)
            return None   
        
        if self.storage_type == 'memory':
            return self.map_int2ext[int_key]
