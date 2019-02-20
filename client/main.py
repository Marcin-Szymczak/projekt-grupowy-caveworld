import shared.world

from shared.drawing import Canvas
from shared.engine import Engine
from shared.state import State
from shared.world import World, Tile
from client.world import Object
from shared.net.cave_world_protocol.protocol import CaveWorldProtocol
from .net.network import ClientNetwork, Connected, Disconnected
from shared.net.cave_world_protocol import \
    actor, client, world

from server.actor import Actor

import asyncio
import websockets
import threading


class Main(State):
    def __init__(self, engine : Engine):
        self.engine = engine
        self.canvas = Canvas(engine.get_renderer())
        
        shared.world.Tile.init_graphics(self.canvas)
        shared.world.Object.init_graphics(self.canvas)

        self.network = ClientNetwork(CaveWorldProtocol())
        self.network.bind({
            Connected: self.on_connected,
            Disconnected: self.on_disconnected,
            actor.ActorResponse: self.on_actor_response,
            actor.PrepareTurnRequest: self.on_prepare_turn_request,
            world.DataResponse: self.on_world_data_response,
        })

        
        self.world = World(self.canvas, 0, 0)
        self.actor = None

    def connect(self, address, port):
        self.network.connect(address, port)

    def on_connected(self, message):
        print("Successfully connected!!!")
        self.network.send(client.Introduction(name="foo"))
        self.network.send(world.DataRequest())
        self.network.send(actor.ActorRequest(type="caveman"))

    def on_disconnected(self, message):
        print("Disconnected from the server...")
        
    def on_world_data_response(self, message):
        print("World data from server")

        self.world.new(message.width, message.height)

        for x, row in enumerate(message.tiles):
            for y, tile in enumerate(row):
                self.world.data[x][y] = Tile(tile.type, tile.z)
                if tile.object:
                    self.world.data[x][y].object = Object(
                        representation=tile.object.repr
                    )

    def on_actor_response(self, message):
        print("Actor response!")
        pass

    def on_prepare_turn_request(self, message):
        print("Prepare turn request!", message.as_dict())
        pass

    def update(self, dt):
        self.network.process()

    def draw(self):
        self.canvas.set_color_rgb(32, 32, 32)
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