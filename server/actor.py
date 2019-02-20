from shared.actor import Actor as SharedActor, Condition
from shared import drawing as draw
from shared.world import Tile
from server.world import Object
from shared.net.cave_world_protocol import actor

import math

class Metabolism:
    """
    The rate at which actor's needs change.
    """
    def __init__(self, hunger_rate, thirst_rate, cold_rate):
        self.hunger_rate = 0
        self.thirst_rate = 0
        self.cold_rate = 0

class Sense:
    def __init__(self, name, range):
        self.name = name
        self.range = range

class Actor(SharedActor, Object):
    def __init__(self, client, world, representation):
        SharedActor.__init__(self)
        Object.__init__(self, representation)

        self.metabolism = Metabolism(0, 0, 0)
        self.senses = {}

        self.client = client
        self.world = world

    def add_sense(self, sense):
        self.senses[sense.name] = sense

    def move_to(self, new_x, new_y):
        self.detach()
        self.x = new_x
        self.y = new_y
        self.attach()

    def attach(self):
        if self.x is None or self.y is None:
            return

        x, y = int(self.x), int(self.y)

        t = self.world.get(x,y)
        if t == None:
            return

        if t.object == None:
            t.object = self

    def detach(self):
        if not self.x or not self.y:
            return False

        x, y = int(self.x), int(self.y)
        t = self.world.get(x, y)
        if t == None:
            return False
            
        if t.object == self:
            t.object = None
            return True
        return False

    def gather_senses_information(self):
        senses = {}
        for x in range(self.world.w):
            for y in range(self.world.h):
                t = self.world.get(x, y)
                if t.object is None:
                    continue
                # import pdb; pdb.set_trace()
                for sense in self.senses.values():
                    if math.pow(self.x-x, 2) + math.pow(self.y-y, 2) > math.pow(sense.range, 2):
                        continue
                    
                    name = sense.name
                    traits = t.object.get_traits(name)
                    if not traits:
                        continue

                    sensation = {
                        "traits": list(traits),
                        "x": x,
                        "y": y
                    }
                    if not name in senses:
                        senses[name] = []
                    senses[name].append(sensation)

        return {
            "sight": senses.get("sight", []),
            "hearing": senses.get("hearing", []),
            "smell": senses.get("smell", [])
        }


class CaveMan(Actor):
    def __init__(self, client, world):
        super().__init__(client, world, "caveman")
        self.add_sense(Sense("sight", 10))
        self.add_sense(Sense("smell", 5))
        self.add_sense(Sense("hearing", 30))
        self.image = self.IMAGES[self.representation()]

    def paint(self, canvas : draw.Canvas):
        canvas.set_color_rgb(255, 255, 255)
        canvas.paint(
            self.image,
            -self.image.w/2,
            -self.image.h)

        canvas.paint_rectangle(-1, -1, 2, 2)

    def representation(self):
        return "caveman"

class Wolf(Actor):
    def __init__(self, client):
        super().__init__(self)
        self.add_sense(Sense("sight", 5))
        self.add_sense(Sense("hearing", 50))
        self.add_sense(Sense("smell", 30))

    def representation(self):
        return "wolf"

class Sheep(Actor):
    def __init__(self, client):
        super().__init__(self)
        self.add_sense(Sense("sight", 5))
        self.add_sense(Sense("hearing", 10))
        self.add_sense(Sense("smell", 10))

    def representation(self):
        return "sheep"
