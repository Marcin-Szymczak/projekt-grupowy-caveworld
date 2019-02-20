from .protocol import * # pylint: disable=unused-wildcard-import
from .model import * # pylint: disable=unused-wildcard-import
import unittest

class SimpleMessage(Message):
    def model(self):
        self.data = Any()
    
class SimpleProtocol(Protocol):
    def wrap(self, message):
        return message.as_dict()

    def unwrap(self, data):
        return SimpleMessage(data)

class TestProtocol(unittest.TestCase):
    def test_wrap_unwrap(self):
        protocol = SimpleProtocol()
        self.assertDictEqual(
            protocol.wrap(SimpleMessage(
                {
                    "data": "Hello!"
                }
            )),
            {
                "data": "Hello!"
            }
        )

        self.assertIsInstance(
            protocol.unwrap(
                {
                    "data": "Hello!"
                }
            ),
            SimpleMessage
        )