from ..protocol import Message
from ..model import * # pylint: disable=unused-wildcard-import

class DataRequest(Message):
    def model(self):
        pass

class Object(Model):
    def model(self):
        self.repr = Type(str)

class Tile(Model):
    def model(self):
        self.type = Type(int)
        self.z = Type(float)
        self.object = Option(Type(Object))
    
class DataResponse(Message):
    def model(self):
        self.width = Type(int)
        self.height = Type(int)
        self.tiles = List(List(Tile))
    