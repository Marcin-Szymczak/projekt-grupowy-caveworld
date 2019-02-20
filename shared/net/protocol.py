from abc import ABC, abstractmethod
from .model import * # pylint: disable=unused-wildcard-import

class Message(Model, ABC):
    """
    A single unit of information to be sent over to the other side.
    When loaded from a 'raw' dict object, the underlying types are validated.
    """
    
class Protocol:
    """
    Protocol class provides the functionality of wrapping and unwrapping
    single messages into "protocol messages", which can be sent over and 
    "unwrapped" on the receiving side.
    """
    @abstractmethod
    def wrap(self, message : Message):
        """
        Wraps the provided message object (subclass of Message) to be sent over
        to the receiving side.
        """
        pass

    @abstractmethod
    def unwrap(self, data):
        """
        Unwraps the received raw data (its structure is dependant on the wrapping
        procedure and fully defined by the protocol) to yield a Message.
        """
        pass