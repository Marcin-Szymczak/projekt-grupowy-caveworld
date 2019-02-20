"""
Abstraction over SDL2 native Renderer functions to easily perform various
drawing operations.
"""

import math

import sdl2
import sdl2.sdlimage as img
import sdl2.sdlttf as ttf
from copy import copy

import ctypes

Color = sdl2.SDL_Color

class Transform:
    def __init__(self):
        self.tx = 0
        self.ty = 0
        self.scalex = 1
        self.scaley = 1

    def translate(self, tx, ty):
        self.tx += tx
        self.ty += ty

    def position(self, x, y):
        return (x + self.tx), (y + self.ty)
    
    def inverse_position(self, x, y):
        return (x - self.tx), (y - self.ty)

    def size(self, w, h):
        return (w, h)

class Canvas:
    """
    A Canvas class which wraps up the SDL2 renderer to provide convenient drawing
    methods. It also supports basic 2d transformations of translating and scaling.
    (They are not matrix-based, but that is by design, because of the limited needs)
    """
    def __init__(self, renderer : sdl2.SDL_Renderer):
        self.renderer = renderer
        self.transform = [Transform()]

    def translate(self, tx, ty):
        """
        Apply a translation transformation. Any further drawing operations will be
        translated by the specified amount.
        Translations can be stacked, their effect is the sum of all previous
        translations
        """
        self.transform[-1].translate(tx, ty)

    def save(self):
        """
        Saves the current transformation state on the stack. Its inverse is the method
        `restore` which pops the saved transformation from the stack.
        """
        self.transform.append(copy(self.transform[-1]))

    def restore(self):
        """
        Pops the topmost transformation from the stack. Its opposite is the `save` method.
        """
        if len(self.transform) > 1:
            self.transform.pop()
        # else:
        # throw

    def get_size(self):
        x = ctypes.c_int(-1)
        y = ctypes.c_int(-1)
        sdl2.SDL_GetRendererOutputSize(self.renderer, ctypes.byref(x), ctypes.byref(y))

        return x.value, y.value


    def set_color_rgb(self, r, g, b, a=255):
        """
        Set the current drawing color by providing a r,g,b,a arguments instead of the
        `SDL_Color` class.
        """
        sdl2.SDL_SetRenderDrawColor(self.renderer, r, g, b, a)

    def set_color(self, color : sdl2.SDL_Color):
        """
        Set the current drawing color.
        """
        sdl2.SDL_SetRenderDrawColor(self.renderer, color.r, color.g, color.b, color.a)

    def sketch_rectangle(self, x, y, w, h):
        """
        Sketches a rectangle's outline on the screen.
        To fill the rectangle use the `paint_rectangle` method.
        """
        x, y = self.transform[-1].position(x, y)
        w, h = self.transform[-1].size(w, h)

        rect = sdl2.SDL_Rect(x, y, w, h)
        sdl2.SDL_RenderDrawRect(self.renderer, rect)

    def paint_rectangle(self, x, y, w, h):
        """
        Paints the whole rectangle on the screen. (It will be filled).
        To only draw its outline, use the `sketch_rectangle` method.
        """
        x, y = self.transform[-1].position(x, y)
        w, h = self.transform[-1].size(w, h)

        rect = sdl2.SDL_Rect(int(x), int(y), int(w), int(h))
        sdl2.SDL_RenderFillRect(self.renderer, rect)

    def paint_texture(self, texture, srcrect, dstrect):
        """
        Paints the specified texture on the screen.
        
        texture - the texture to be painted
        srcrect - the rectangle of the texture's region to be painted
        dstrect - the rectangle of the screen's region to apply the texture onto.
        """
        if srcrect is not None:
            srcrect.x, srcrect.y = self.transform[-1].position(srcrect.x, srcrect.y)
            srcrect.w, srcrect.h = self.transform[-1].size(srcrect.w, srcrect.h)
        
        if dstrect is not None:
            dstrect.x, dstrect.y = self.transform[-1].position(dstrect.x, dstrect.y)
            dstrect.w, dstrect.h = self.transform[-1].size(dstrect.w, dstrect.h)

        sdl2.SDL_RenderCopy(self.renderer, texture, srcrect, dstrect)

    def paint(self, drawable, *args, **kvargs):
        """
        Paints a drawable object.

        A drawable object is expected to implement a `paint` method which takes the
        canvas as its first argument.
        """
        drawable.paint(self, *args, **kvargs)
    
    def set_scale(self, sx, sy):
        """
        Sets the scaling factor for further drawing operations.
        """
        sdl2.SDL_RenderSetScale(self.renderer, sx, sy)

    def clear(self):
        """
        Clears the canvas with the current color.

        Color can be chnages by
        - `set_color`
        - `set_color_rgb`
        """
        
        sdl2.SDL_RenderClear(self.renderer)

class Image:
    """
    A 2d image which contains its SDL_Surface and SDL_Texture data.

    It can be loaded from a specified file name and its texture will be automatically
    created.

    It can be painted on a canvas by specifying the x,y coordinates of the top-left
    corner.
    """
    def __init__(self):
        self.surface = None
        self.texture = None
        self.w = None
        self.h = None

    def __del__(self):
        """
        Called when the image is not longer needed and freed by the Garbage Collector.
        It will try to free the resources it holds onto.
        """
        self.free()

    def load(self, path, canvas : Canvas):
        """
        Load the image from the specified filename.
        """
        self.surface = img.IMG_Load(str.encode(path))
        self.w = self.surface.contents.w
        self.h = self.surface.contents.h
        self.texture = sdl2.SDL_CreateTextureFromSurface(canvas.renderer, self.surface)

    def free(self):
        """
        Free the image's data. Should be called when it is not needed anymore.
        """
        if self.surface != None:
            sdl2.SDL_FreeSurface(self.surface)
        if self.texture != None:
            sdl2.SDL_DestroyTexture(self.texture)

    def paint(self, canvas, x, y):
        """
        Paint the image with its top-left corner residing in the x,y coordinates provided.
        """
        x, y = canvas.transform[-1].position(x, y)
        w, h = self.w, self.h#canvas.transform[-1].size(self.w, self.h)
        dstrect = sdl2.SDL_Rect(
            x = int(x),
            y = int(y), 
            w = int(self.w), 
            h = int(self.h))
        sdl2.SDL_RenderCopy(canvas.renderer, self.texture, None, dstrect)

class Frame:
    """
    A single frame from an image atlas.
    """
    def __init__(self, image, x, y, w, h):
        self.image = image
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def paint(self, canvas, x, y):
        """
        Paints the frame with its top-left corner at the x,y.
        """
        x, y = canvas.transform[-1].position(x, y)
        srcrect = sdl2.SDL_Rect(x = self.x, y = self.y, w = self.w, h = self.h)
        dstrect = sdl2.SDL_Rect(x = int(x), y = int(y), w = self.w, h = self.h)
        sdl2.SDL_RenderCopy(canvas.renderer, self.image.texture, srcrect,
            dstrect)

class Atlas:
    """
    An image atlas. Whenever an image is just a collection of smaller frames, this atlas
    can be used to manage such image.
    It provides options for extracting single frames from such atlas and to draw them
    individually.
    """
    def __init__(self, path = None):
        self.image = None
        self.columns = None
        self.rows = None
        self.frame_w = None
        self.frame_h = None

    def __del__(self):
        if self.image:
            self.free()

    def load(self, path, frame_w, frame_h, canvas : Canvas):
        """
        Load an image which is an image atlas.
        path - filename of the image.
        frame_w - the width of a single frame (column width)
        frame_h - the height of a single frame (row height)
        canvas - the canvas which should be used to load the image.
        """
        self.image = Image()
        self.image.load(path, canvas)
        self.columns = self.image.w/frame_w
        self.rows = self.image.h/frame_h
        self.frame_w = frame_w
        self.frame_h = frame_h

    def get_frame(self, id):
        """
        Get a single frame based on its id.
        
        Frames are counted starting from 0 and increasing when going right, row after
        row.
        """
        x = (id % self.columns)*self.frame_w
        y = math.floor(id / self.columns)*self.frame_h
        w = self.frame_w
        h = self.frame_h

        return Frame(
            image = self.image,
            x = int(x),
            y = int(y),
            w = int(w),
            h = int(h)
        )
    
    def free(self):
        """
        Frees the resources.
        """
        self.image.free()


'''
class Painting:
    """
    ??? Do rozkminienia po co :)
    """
    def __init__(self, image):
        self.x = 0
        self.y = 0
        self.image = image

    def paint(self, canvas):
        self.image.draw(canvas.renderer, self.x, self.y)
'''
class Font:
    """
    Font which allows for creating text with it.
    """
    def __init__(self, path, size):
        self._font = ttf.TTF_OpenFont(bytes(path, "utf8"), size)
        self.size = size

    @property
    def handle(self):
        return self._font

class Text:
    """
    A single text drawn with its font.
    Whenever new text is written to this object by means of the
    `text` field, its graphical representation will be refreshed, so it is most efficient
    to set the text once and only keep painting it.
    """
    def __init__(self, canvas : Canvas, font=None, text=None):
        self.font = font
        self._text = text # The string which holds the drawn text. NOT the graphical repr.
        self.texture = None
        self.canvas = canvas
        self.surface_size = None

        if font is not None and text is not None:
            self.refresh()

    def refresh(self):
        """
        Refreshes the graphical representation of stored text.
        """
        surface = ttf.TTF_RenderUTF8_Blended(self.font.handle, bytes(self._text, "utf8"), sdl2.SDL_Color(255,255,255,255))
        if not surface:
            self.surface_size = (0,0)
            return
        self.surface_size = (surface.contents.w, surface.contents.h)
        self.texture = sdl2.SDL_CreateTextureFromSurface(self.canvas.renderer, surface)
        sdl2.SDL_SetTextureBlendMode(self.texture, sdl2.SDL_BLENDMODE_BLEND)
        sdl2.SDL_FreeSurface(surface)
    
    def paint(self, canvas, x, y, alignment='top_left'):
        """
        Paints the text at the x,y coordinates provided with chosen alignment:
        - top_left
        - center_left
        - center
        """
        w, h = self.surface_size

        if alignment == 'top_left':
            pass
        elif alignment == "center_left":
            y -= h/2
        elif alignment == 'center':
            x -= w/2
            y -= h/2

        rect = sdl2.SDL_Rect(x=int(x), y=int(y), w=int(w), h=int(h))
        
        # sdl2.SDL_RenderCopy(canvas.renderer, self.texture, None, rect)
        canvas.paint_texture(self.texture, None, rect)

    @property
    def text(self):
        """
        Gets the current text string.
        """
        return self._text
    
    @text.setter
    def text(self, new_text):
        """
        Sets new text string.
        """
        self._text = new_text
        self.refresh()