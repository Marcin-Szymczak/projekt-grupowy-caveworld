import asyncio
import json
import websockets

from queue import Queue, Empty
from threading import Thread

from shared.net.network.network import Network
from shared.net.protocol import Protocol

class ClientConnected:
    """
    Marker class for binding the client connection event to a callback
    """
    pass

class ClientDisconnected:
    """
    Marker class for binding to the client disconnection event.
    """
    pass

class Client:
    def __init__(self, id, websocket):
        self.id = id
        self.websocket = websocket
        self.send_queue = Queue()
        self.userdata = {}

    def __getitem__(self, key):
        return self.userdata[key]

    def __setitem__(self, key, value):
        self.userdata[key] = value

    def __contains__(self, key):
        return key in self.userdata

    def _send_data(self, data):
        # await self.websocket.send(data)
        self.send_queue.put(data)

    async def recv(self, data):
        await self.websocket.recv()

    async def sender(self, network):
        while True:
            await asyncio.sleep(0.01)
            try:
                item = self.send_queue.get_nowait()
                await self.websocket.send(item)

            except Empty:
                pass

    async def receiver(self, network):
        while True:
            network.receive(self, await self.websocket.recv())

    def __repr__(self):
        return f"Client({self.id})"

class ServerNetwork(Network):
    def __init__(self, protocol : Protocol):
        super().__init__()

        self.thread = None
        self.clients = []

        self.protocol = protocol
        self.receive_queue = Queue()

    def send_to(self, client, message):
        packet = self.protocol.wrap(message)
        client._send_data(json.dumps(packet))
    
    def send_to_id(self, client_id, message):
        self.send_to(self.clients[client_id], message)
    
    def broadcast(self, message):
        for client in self.clients:
            if client is None:
                continue
                
            self.send_to(client, message)

    def receive(self, client, data):
        message = self.protocol.unwrap(json.loads(data))
        self.receive_queue.put((client, message))

    def receive_message(self, client, message):
        self.receive_queue.put((client, message))

    def host(self, address,port):
        def thread():
            asyncio.set_event_loop(asyncio.new_event_loop())
            server = websockets.serve(self.handle_client_connection, address, port)
            asyncio.get_event_loop().run_until_complete(server)
            asyncio.get_event_loop().run_forever()

        self.thread = Thread(target=thread)
        self.thread.start()

    def process(self):
        while not self.receive_queue.empty():
            client, message = self.receive_queue.get()
            self.call(message, client)

    async def handle_client_connection(self, ws, path):
        id = 0
        for c in self.clients:
            if c is None:
                break
            id += 1
        else:
            self.clients.append(None)

        c = Client(id, ws)
        self.clients[id] = c

        self.receive_message(c, ClientConnected())
        
        try:
            await asyncio.gather(
                c.sender(self),
                c.receiver(self)
            )
        except websockets.exceptions.ConnectionClosed:
            self.receive_message(c, ClientDisconnected())
            self.clients[id] = None