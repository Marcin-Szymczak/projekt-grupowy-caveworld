"""
Shared implementation of World, which is a 2d array of Tiles and each tile
can contain an Object.
"""

from shared import drawing as draw
from random import randint, random
import math
from abc import ABC, abstractmethod

class Object(ABC):
    """
    Represents an object which is present in the World.
    On the client side this is only extended to keep the image to be drawn
    with. On the server side it can be any class deriving from Object.
    """

    """
    Supported image 'names' or *representations*
    """
    IMAGE_PATHS = {
        "caveman": "resource/image/agent.png",
        "fruit_red": "resource/image/fruit_red.png",
        "fruit_green": "resource/image/fruit_green.png",
        "fruit_purple": "resource/image/fruit_purple.png",
        "stone": "resource/image/stone.png"
    }

    """
    To be filled with Image classess upon calling `init_graphics`
    """
    IMAGES = {}

    @classmethod
    def init_graphics(CLASS, canvas):
        """
        Initializes the graphics used by any object by taking paths from
        `IMAGE_PATHS` and loading the images to `IMAGES` with the same key
        """
        for name, path in CLASS.IMAGE_PATHS.items():
            image = draw.Image()
            image.load(path, canvas)
            CLASS.IMAGES[name] = image
        
    @abstractmethod
    def paint(self, canvas):
        """
        The implementations needs to draw itself as if the ground is on the
        0,0 coordinates
        """
        pass

    @abstractmethod
    def representation(self):
        """
        Should return any name of the "IMAGES" above, to have a consistent
        representation on the client and server side.
        """
        pass

class Tile:
    """
    A single tile on the world map, stores its type, its height and the object
    which is currently on this tile (there can be a maximum of 1 object
    per tile).

    """
    image = None
    image_path = "resource/image/tiles.png"
    tile_frame_w = 16
    tile_frame_h = 16
    tile_w = 15
    tile_h = 8
    tile_base_h = 16

    def __init__(self, type, z=None):
        self.type = type
        self.object = None
        self.z = z or 0.0

    @staticmethod
    def to_screen_coords(x, y, z=0):
        """
        Transforms the provided coordinates from tile-space, in which the
        coordinates (except z) are integers and are counted in Tiles into
        screen-space coordinates which are pixels on the screen.
        """
        x = int(x*Tile.tile_w-y*Tile.tile_h)
        y = int((y/2)*Tile.tile_h+z)

        return (x,y)
    
    @staticmethod
    def init_graphics(canvas):
        """
        Initializes the tile graphics for this class.
        """
        Tile.image = draw.Atlas()
        Tile.image.load(Tile.image_path, Tile.tile_frame_w, Tile.tile_frame_h, canvas)


class World:
    """
    The world is a 2d array of tiles, which can contain objects that are
    currently on them.
    """
    def __init__(self, canvas, width, height):
        self.w = None
        self.h = None
        self.data = None

        self.new(width, height)

    def new(self, width, height):
        """
        Creates a new world with the specified size.
        """
        self.w = width
        self.h = height
        self.data = [
            [Tile(0) for _ in range(height)] 
            for _ in range(width)
        ]

    def get(self, x, y):
        if x < 0 or x >= self.w or y < 0 or y >= self.h:
            return None
        return self.data[x][y]
        
    def draw(self, canvas : draw.Canvas):
        """
        Draws every tile (and its contents) in correct order.
        """
        scr_w, scr_h = canvas.get_size()
        for y in range(self.h):
            for x in range(self.w):
                tile = self.data[x][y]

                draw_x, draw_y = Tile.to_screen_coords(x, y, tile.z)
                real_x, real_y = canvas.transform[-1].position(draw_x, draw_y)

                if real_x < -Tile.tile_w or real_x > scr_w + Tile.tile_w \
                    or real_y < -Tile.tile_h or real_y > scr_h + Tile.tile_h:
                    
                    continue

                frame = Tile.image.get_frame(
                    tile.type
                )

                canvas.paint(frame, draw_x, draw_y)
                if tile.object is not None:
                    canvas.save()
                    canvas.translate(
                        draw_x + Tile.tile_w/2,
                        draw_y + Tile.tile_h/2
                    )
                    canvas.paint(tile.object)
                    canvas.restore()
                canvas.set_color_rgb(255,0,255)