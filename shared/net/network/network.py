from abc import ABC, abstractmethod

class Network(ABC):
    """
    Abstract class for Network, which is responsible for maintaining
    a connection/serving the network and call the registered callbacks upon
    receiving bound messages.

    Argument names nomenclature is:
    message - a proper message object
    data - a raw or wrapped by protocol, data, which should be unwrapped to use
    protocol - responsible for wrapping and unwrapping messages. Currently
        the only protocol implementation adds an ID to every message, to be
        correctly constructed on the receiving side.
    """
    
    def __init__(self):
        self.callbacks = {}

    def bind(self, bindings : dict):
        self.callbacks.update(bindings)

    def call(self, message, *args, **kvargs):
        if message.__class__ in self.callbacks:
            self.callbacks[message.__class__](message, *args, **kvargs)

    @abstractmethod
    def process(self):
        """
        Process the incoming messages and call their associated callbacks.
        """
        pass