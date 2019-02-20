from .. import protocol
from . import \
    actor, client, world

class CaveWorldProtocol(protocol.Protocol):
    """
    Implementation of the application's protocol. Provides a unique ID for every
    message to be sent over, to be uniquely identified.

    Wrapping the message corresponds to acquiring the id of the message and then
    constructing a dict like: 
    {
        "id": id,
        "message": message.as_dict()
    }

    Unwrapping does the opposite.

    Every message is numbered by the call to `messages` method, which register
    (or replace) message types.
    
    There should be one and only 1 call to `messages` in this file.
    """
    MESSAGE_ID = {}
    ID_MESSAGE = {}

    @classmethod
    def messages(c, *message_types : list):
        """
        Defines the message id's to be used in the protocol.

        Any message which is not declared in the call to this function can't
        be sent over by this protocol.
        """

        for i, t in enumerate(message_types):
            c.MESSAGE_ID[t] = i
            c.ID_MESSAGE[i] = t

    @classmethod
    def get_id_from_message(c, message):
        """
        Returns the id of the provided message object by looking up its class.

        Throws when the message is not associated in the protocol (it was not
        declared in call to `messages`).
        """
        return c.MESSAGE_ID[message.__class__]
    
    @classmethod
    def get_message_from_id(c, id):
        """
        Returns the message class from the id provided.

        Throws when the message is not associated in the protocol (it was not
        declared in call to `messages`).
        """
        return c.ID_MESSAGE[id]

    def wrap(self, message):
        id = self.get_id_from_message(message)

        return {
            "id": id,
            "message": message.as_dict()
        }

    def unwrap(self, raw : dict):
        id = raw["id"]
        message_class = self.get_message_from_id(id)
        return message_class(raw["message"])

CaveWorldProtocol.messages(
    # Actor
    actor.ActorRequest,
    actor.ActorResponse,
    actor.PrepareTurnRequest,
    actor.TurnRequest,
    actor.TurnResult,

    # Client
    client.IntroductionRequest,
    client.Introduction,

    # World
    world.DataResponse,
    world.DataRequest
)

print("CaveWorld protocol:")
for k, v in CaveWorldProtocol.ID_MESSAGE.items():
    print(k,":", v)