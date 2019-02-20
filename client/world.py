from shared import drawing as draw
from shared.world import Object as SharedObject, Tile

class Object(SharedObject):
    def __init__(self, representation):
        self._representation = representation
        self.image = self.IMAGES[representation]

    def paint(self, canvas):
        canvas.set_color_rgb(255, 255, 255)
        canvas.paint(
            self.image,
            -self.image.w/2, 
            -self.image.h
        )

    def representation(self):
        return self._representation