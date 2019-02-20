from ..protocol import Message
from ..model import * # pylint: disable=unused-wildcard-import

class IntroductionRequest(Message):
    def model(self):
        pass

    def __repr__(self):
        return f"IntroductionRequest()"

class Introduction(Message):
    def model(self):
        self.name = Type(str)

    def __repr__(self):
        return f"Introduction(name={self.name})"