import uuid

class ID_Mapper():
    def __init__(self):
        self.map_ext2int = {}
        self.map_int2ext = {}

    def ext2int(self, ext_type, ext_id):
        if ext_type not in self.map_ext2int.keys(): self.map_ext2int[ext_type] = {}

        try:
            int_key = self.map_ext2int[ext_type][ext_id]
        except:
            int_key = str(uuid.uuid1())
            self.map_ext2int[ext_type][ext_id] = int_key
            self.map_int2ext[int_key] = (ext_type, ext_id)
        return int_key

    def int2ext(self, int_key):
        return self.map_int2ext[int_key]