from shared.net.cave_world_protocol.world import DataResponse as WorldDataResponse
from shared.world import World as SharedWorld, Object as SharedObject
from abc import ABC, abstractmethod
import math
from random import random, randint, choice
from shared import drawing as draw

class Object(SharedObject):
    def __init__(self, representation):
        self.traits = {}
        self._representation = representation
        self.image = self.IMAGES[representation]

    def paint(self, canvas : draw.Canvas):
        canvas.set_color_rgb(255, 255, 255)
        canvas.paint(self.image, -self.image.w/2, -self.image.h)

    def representation(self):
        return self._representation

    def on_eat(self, actor):
        return False

    def on_pick_up(self, actor):
        return False

    def on_destroy(self, actor):
        return False

    def get_traits(self, sense):
        return self.traits.get(sense, set())

class EdibleFruit(Object):
    def __init__(self):
        super().__init__("fruit_green")
        self.traits = {
            "sight": {"small", "round", "green"},
            "smell": {"sweet", "fresh"},
            "hearing": set()
        }

class PoisonousFruit(Object):
    def __init__(self):
        super().__init__("fruit_red")
        self.traits = {
            "sight": {"small", "round", "red"},
            "smell": {"bitter", "rotten"},
            "hearing": set()
        }

class Stone(Object):
    def __init__(self):
        super().__init__("stone")
        self.traits = {
            "sight": {"small", "rough", "gray"},
            "smell": set(),
            "hearing": set()
        }

class World(SharedWorld):
    def generate(self):
        """
        Mutates the world's data with the specified algorithm to make it varied
        """
        ph = random()*2*math.pi
        for x in range(self.w):
            for y in range(self.h):
                t = (x+y)/math.pi/2+ph

                tile = self.data[x][y]
                tile.type = randint(0,2)
                tile.z = round(math.sin(t)*8)

                if random() < 0.2:
                    tile.object = choice([
                        EdibleFruit, PoisonousFruit, Stone
                    ])()
    
    def construct_world_data_response(self):
            tiles = []
            for r in self.data:
                row = []
                for t in r:
                    o = None
                    if t.object:
                        o = {
                            "repr": t.object.representation()
                        }

                    row.append({
                            "type": int(t.type),
                            "z": float(t.z),
                            "object": o
                    })
                tiles.append(row)

            return WorldDataResponse(
                width=self.w,
                height=self.h,
                tiles=tiles
            )