from .protocol import *
from . import client
import unittest

class TestCaveWorldProtocol(unittest.TestCase):
    def test_protocol(self):
        protocol = CaveWorldProtocol()
        message = client.Introduction(name="foo")
        _id = protocol.get_id_from_message(message)

        self.assertDictEqual({
            "id": _id,
            "message": {
                "name": "foo"
                }
            },
            protocol.wrap(message)
        )
        
