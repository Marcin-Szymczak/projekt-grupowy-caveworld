import asyncio
import json
import websockets

from shared.net.network.network import Network
from shared.net.protocol import Protocol

from queue import Queue, Empty
from threading import Thread

class Connected:
    """
    Marker message which gets 'emitted' upon successful connection.
    """

class Disconnected:
    """
    Marker message which gets 'emitted' upon successful connection.
    """

class ClientNetwork(Network):
    def __init__(self, protocol : Protocol):
        super().__init__()
        self.thread = None
        self.protocol = protocol

        self.receive_queue = Queue()
        self.send_queue = Queue()

    async def receiver(self, ws):
        while True:
            msg = await ws.recv()
            self.receive(msg)

    async def sender(self, ws):
        while True:
            await asyncio.sleep(0.01)
            try:
                msg = self.send_queue.get_nowait()
                await ws.send(msg)
            except Empty:
                pass

    def receive(self, data):
        """
        Called when raw protocol data gets received and should be
        unwrapped by the corresponding protocol.
        """

        message = self.protocol.unwrap(json.loads(data))
        self.receive_queue.put(message)

    def receive_message(self, message):
        """
        Called when a proper message was received, and is supposed to
        be processed without any unwrapping.
        """
        self.receive_queue.put(message)

    def send(self, message):
        data = self.protocol.wrap(message)
        print("Sending", data)
        self.send_queue.put(json.dumps(data))
    

    def connect(self, address, port):
        async def client():
            async with websockets.connect(f"ws://{address}:{port}") as ws:
                print("Successfully connected!")

                self.receive_message(Connected())

                await asyncio.gather(
                    self.sender(ws),
                    self.receiver(ws)
                )

                self.receive_message(Disconnected())
            
        def thread():
            asyncio.set_event_loop(asyncio.new_event_loop())
            asyncio.get_event_loop().run_until_complete(client())
        
        self.thread = Thread(target=thread)
        self.thread.start()

    def process(self):
        while True:
            try:
                message = self.receive_queue.get_nowait()
                self.call(message)
            except Empty:
                break