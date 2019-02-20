import websockets
import asyncio
import threading

import server.actor
import shared.world

from .net.network import \
    ServerNetwork, ClientConnected, ClientDisconnected

from shared.engine import Engine
from shared.drawing import Canvas
from shared.net.cave_world_protocol import \
    actor, client, world
from shared.net.cave_world_protocol.protocol import CaveWorldProtocol
from shared.state import State
from server.turn import TurnManager
from server.world import World
from queue import Queue, Empty

class Main(State):
    def __init__(self, engine : Engine):
        self.engine = engine
        self.canvas = Canvas(engine.get_renderer())

        shared.world.Tile.init_graphics(self.canvas)
        shared.world.Object.init_graphics(self.canvas)

        self.connection = None
        self.thread = None
        self.network = ServerNetwork(CaveWorldProtocol())
        self.network.bind({
            ClientConnected: self.on_client_connected,
            ClientDisconnected: self.on_client_disconnected,
            client.Introduction: self.on_client_introduction,
            actor.ActorRequest: self.on_actor_request,
            world.DataRequest: self.on_world_request
        })

        self.turn_manager = TurnManager(self)

        self.world = World(self.canvas, 32, 32)
        self.world.generate()

    def on_client_introduction(self, message, client):
        print("Client introduction!")
        print("message: ", message)

    def on_client_connected(self, message, client):
        print("Client connected!", client)

    def on_client_disconnected(self, message, client):
        print("Client disconnected!", client)
        if "actor" in client:
            self.turn_manager.unregister_client(client)
            if not client["actor"].detach():
                print("Error detaching actor!")
            self.network.broadcast(self.world.construct_world_data_response())

    def on_world_request(self, message, client):
        print('Client', client, 'requests world data!')
        self.network.send_to(client, self.world.construct_world_data_response())

    def on_actor_request(self, message, client):
        from random import randint

        while True:
            x, y = randint(0, self.world.w-1), randint(0, self.world.h-1)
            
            if self.world.data[int(x)][int(y)].object is None:
                break

        from server.actor import CaveMan
        actor = CaveMan(client, self.world)
        actor.x = x
        actor.y = y
        client["actor"] = actor

        print("Created actor at",x, y)
        actor.attach()
        self.turn_manager.register_actor(actor)

        self.network.broadcast(self.world.construct_world_data_response())


    def host(self, address, port):
        self.network.host(address, port)

    def update(self, dt):
        self.network.process()

    def draw(self):
        self.canvas.set_color_rgb(0, 0, 0)
        self.canvas.clear()

        self.canvas.save()
        self.canvas.set_scale(3, 3)
        self.canvas.translate(512, 512)
        x, y = self.engine.mouse_position()
        self.canvas.translate(-x*2, -y*2)
        self.world.draw(self.canvas)

        self.canvas.restore()

    def key_pressed(self, key):
        pass

    def key_released(self, key):
        pass

    def mouse_pressed(self, x, y, button):
        pass
    
    def mouse_released(self, x, y, button):
        pass