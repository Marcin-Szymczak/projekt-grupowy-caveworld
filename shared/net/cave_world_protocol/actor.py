from ..protocol import Message
from ..model import * # pylint: disable=unused-wildcard-import

class Condition(Model):
    def model(self):
        self.hunger = Type(float)
        self.thirst = Type(float)
        self.temperature = Type(float)
        self.health = Type(float)

class Sensation(Model):
    def model(self):
        self.traits = List(Type(str))
        self.x = Type(int)
        self.y = Type(int)

class Senses(Model):
    def model(self):
        self.sight = List(Sensation)
        self.hearing = List(Sensation)
        self.smell = List(Sensation)

class Actor(Model):
    def model(self):
        self.type = Type(str)
        self.x = Type(int)
        self.y = Type(int)

        self.senses = Type(Senses)
        self.condition = Type(Condition)

class ActorRequest(Message):
    def model(self):
        self.type = Enum("caveman")

    def __repr__(self):
        return f"PlayerRequest"

class ActorResponse(Message):
    def model(self):
        self.success = Type(bool)
        self.actor = Type(Actor)

    def __repr__(self):
        return f"PlayerResponse"

class PrepareTurnRequest(Message):
    def model(self):
        self.actor = Type(Actor)

class TurnRequest(Message):
    def model(self):
        pass

class TurnResult(Message):
    def model(self):
        self.success = Type(bool)
        self.error = Option(Type(str))