"""
Basic user interface which allows for automatic laying out.
It is powered by SDL2 to provide the renderering and input functionality.
"""
from shared import drawing as draw
from shared.engine import Engine

from collections import namedtuple

import sdl2

class Style:
    """
    A set of styling instructions to draw the current User Interface.

    It consists of field containing the colors of each aspect of the interface.
    """
    def __init__(self, fg, bg, text, accent, border, highlight, depress, shadow):
        self.fg = fg
        self.bg = bg
        self.text = text
        self.accent = accent
        self.border = border
        self.highlight = highlight
        self.depress = depress
        self.shadow = shadow

Style.default = Style(
    fg = draw.Color(192, 192, 192, 255),
    bg = draw.Color(148, 148, 148, 255),
    text = draw.Color(16, 16, 16, 255),
    accent = draw.Color(115, 180, 255),
    border = draw.Color(32, 32, 32, 255),
    highlight = draw.Color(255, 255, 255, 32),
    depress = draw.Color(32, 32, 32, 32),
    shadow = draw.Color(40, 40, 40, 40)
)

Padding = namedtuple('Padding', ['top','right','bottom','left'])

class Element:
    """
    Base class of all elements.
    """
    def __init__(self, ui, style=None, parent=None,
                 x = None, y = None, w = None, h = None):
        self.x = x or 0
        self.y = y or 0
        self.screen_x = 0
        self.screen_y = 0
        self.padding = Padding(top=0, right=0, bottom=0, left=0)
        self.w = w or 0
        self.h = h or 0
        self.mouse_hover = False
        self.mouse_button = {
            "left": False,
            "right": False,
            "middle": False,
            "x1": False,
            "x2": False
        }
        self.clean = False
        self.valid = True
        self.children = []
        self.ui = ui
        self.parent = parent
        self.style = style
        self.uid = None

    def add(self, elementType, *args, **kvargs):
        el = elementType(ui=self.ui, style=self.style, parent=self, *args, **kvargs)
        el.uid = self.ui.get_uid()
        self.children.append(el)

        return el

    def draw(self, canvas):
        pass

    def draw_recursive(self, canvas):
        """
        Internal function which recursively draws the element and all of its children.
        """
        canvas.save()
        canvas.translate(self.x, self.y)
        self.draw(canvas)
        for el in self.children:
            el.draw_recursive(canvas)
        canvas.restore()

    def update(self, dt):
        pass

    def update_recursive(self, dt):
        if self.valid == False:
            self.children = []
            if self.parent:
                self.parent.remove_element(self)
            else:
                self.ui.remove_element(self)

        mx, my = self.ui.screen.engine.mouse_position()
        
        
        if mx >= self.screen_x and mx < self.screen_x + self.w \
           and my >= self.screen_y and my < self.screen_y + self.h:
            self.mouse_hover = True
            if self.ui._mouse_hover == None or self.ui._mouse_hover == self.parent:
                self.ui._mouse_hover = self
        else:
            self.mouse_hover = False

        for el in self.children:
            el.screen_x = self.screen_x + el.x
            el.screen_y = self.screen_y + el.y
            el.updateRecursively(dt)
            if el.mouse_hover:
                self.mouse_hover = False
        
        self.update(dt)

        if not self.clean:
            self.cleanUp()

    def remove(self):
        self.valid = False
        if self.parent:
            self.parent.clean = False

    def remove_element(self, el):
        self.children.remove(el)
        el.parent = None

    def cleanUp(self):
        self.clean = True

    def mouse_pressed(self, x, y, button):
        pass

    def mouse_released(self, x, y, button):
        pass
    
    def key_pressed(self, key):
        pass

    def key_released(self, key):
        pass

    def text_input(self, text):
        pass

    def get_mouse_position(self):
        mx, my = self.ui.screen.engine.mouse_position()

        return mx - self.screen_x, my - self.screen_y
        
class UI():
    """
    Holds all of the ui elements and forward input events to them.
    """
    def __init__(self, screen, style = None):
        self.keyboard_focus = None
        self._mouse_hover = None
        self._mouse_pressed = {
            "left": None,
            "right": None,
            "middle": None,
            "x1": None,
            "x2": None
        }
        self.elements = []
        self.screen = screen
        self.canvas = screen.canvas
        self.font = draw.Font("resource/font/UbuntuMono-R.ttf", 14)
        self.style = None
        self.uid = 0

        if style is None:
            self.style = Style.default

    def get_uid(self):
        result = self.uid
        self.uid += 1

        return result

    def add(self, elementType, *args, **kvargs):
        el = elementType(ui=self, style=self.style, *args, **kvargs)
        el.uid = self.get_uid()
        self.elements.append(el)

        return el

    def draw(self):
        for el in self.elements:
            el.draw_recursive(self.canvas)

    def update(self, dt):
        self._mouse_hover = None
        for el in self.elements:
            el.screen_x = el.x
            el.screen_y = el.y
            el.update_recursive(dt)

    def mouse_pressed(self, x, y, button):
        el = self._mouse_hover
        if el is not None:
            print(f"Mouse pressed on {self._mouse_hover.uid}")
            if self.keyboard_focus and el != self.keyboard_focus:
                self.release_keyboard()

            el.mouse_button[button] = True
            self._mouse_pressed[button] = el
            el.mouse_pressed(x - el.screen_x, y - el.screen_y, button)

    def mouse_released(self, x, y, button):
        if self._mouse_pressed[button] is not None:
            self._mouse_pressed[button].mouse_button[button] = False
            self._mouse_pressed[button].mouse_released(x, y, button)
        self._mouse_pressed[button] = None

    def text_input(self, text):
        if self.keyboard_focus is not None:
            self.keyboard_focus.text_input(text)

    def key_pressed(self, key):
        if self.keyboard_focus is not None:
            self.keyboard_focus.key_pressed(key)
    
    def key_released(self, key):
        if self.keyboard_focus is not None:
            self.keyboard_focus.key_released(key)

    def remove_element(self, element):
        self.elements.remove(element)

    def acquire_keyboard(self, element):
        self.keyboard_focus = element
        self.screen.engine.start_text_input()

    def release_keyboard(self):
        self.keyboard_focus = None
        self.screen.engine.stop_text_input()


class FrameHeader(Element):
    def __init__(self, ui, style=None, parent=None):
        super().__init__(ui, style, parent)
        self._title = draw.Text(canvas = ui.canvas, font = ui.font, text = "")
        self.grab = None

    def draw(self, canvas : draw.Canvas):
        canvas.set_color(self.style.border)
        canvas.paint_rectangle(0, 0, self.w, self.h)

        canvas.set_color(self.style.accent)
        canvas.paint_rectangle(1, 1, self.w-2, self.h-2)

        canvas.set_color(self.style.text)
        self._title.paint(canvas, x = 4, y = self.h/2, alignment="center_left")

    def mouse_pressed(self, x, y, button):
        self.grab = (x, y)

    def mouse_released(self, x, y, button):
        self.grab = None

    def update(self, dt):
        if self.grab is not None:
            mx, my = self.get_mouse_position()

            self.parent.x = self.parent.x + mx - self.x - self.grab[0]
            self.parent.y = self.parent.y + my - self.y - self.grab[1]

    @property
    def title(self):
        return self._title.text
    
    @title.setter
    def title(self, new_title):
        self._title.text = new_title

class Frame(Element):
    def __init__(self, title=None, *args, **kvargs):
        super().__init__(*args, **kvargs)
        self.padding = self.padding._replace(
            top=24,
            left=4,
            right=4,
            bottom=4)

        self.header = self.add(FrameHeader)

        if title is not None:
            self.title = title

    @property
    def title(self):
        return self.header.title

    @title.setter
    def title(self, new_title):
        self.header.title = new_title

    def draw(self, canvas : draw.Canvas):
        canvas.set_color(self.style.border)
        canvas.sketch_rectangle(0, 0, self.w, self.h)
        canvas.set_color(self.style.bg)
        canvas.paint_rectangle(1, 1, self.w-2, self.h-2)

    def cleanUp(self):
        super().cleanUp()

        self.header.x = 0
        self.header.y = 0
        self.header.w = self.w
        self.header.h = self.padding.top - 4

class Button(Element):
    def __init__(self, ui, text = None, style=None, parent=None, *args, **kvargs):
        super().__init__(ui, style, parent, *args, **kvargs)

        self.on_click = None
        self.on_release = None
        self.enabled = True

        self._text = draw.Text(
            canvas = ui.canvas,
            font = ui.font,
            text = text or "")

    @property
    def text(self):
        return self._text.text
    
    @text.setter
    def text(self, new_text):
        self._text.text = new_text

    def mouse_pressed(self, x, y, button):
        if not self.enabled:
            return

        if self.on_click:
            self.on_click(self)

    def mouse_released(self, x, y, button):
        if not self.enabled:
            return

        if self.on_release and self.mouse_hover:
            self.on_release(self)

    def draw(self, canvas : draw.Canvas):
        canvas.set_color(self.style.border)
        canvas.sketch_rectangle(0, 0, self.w, self.h)
        canvas.set_color(self.style.fg)
        canvas.paint_rectangle(1, 1, self.w-2, self.h-2)
        canvas.set_color(self.style.shadow)
        canvas.paint_rectangle(1, self.h-1-4, self.w-2, 4)
        canvas.set_color(self.style.highlight)
        canvas.paint_rectangle(1, 1, self.w-2, 4)
        canvas.set_color(self.style.text)
        self._text.paint(canvas, self.w/2, self.h/2, alignment='center')

        if self.enabled:
            if self.mouse_button["left"]:
                canvas.set_color(self.style.depress)
                canvas.paint_rectangle(1, 1, self.w-2, self.h-2)
            elif self.mouse_hover:
                canvas.set_color(self.style.highlight)
                canvas.paint_rectangle(1, 1, self.w-2, self.h-2)
        else:
            canvas.set_color(self.style.shadow)
            canvas.paint_rectangle(1, 1, self.w-2, self.h-2)

class TextInput(Element):
    def __init__(self, ui, style=None, parent=None, *args, **kvargs):
        super().__init__(ui, style, parent, *args, **kvargs)
        self._text = draw.Text(canvas = ui.canvas, font = ui.font, text = "")

        self.enabled = True

        self.on_input_finished = None
        self.on_character_typed = None
        self.on_input_escaped = None


    @property
    def text(self):
        return self._text.text
    @text.setter
    def text(self, new_text):
        self._text.text = new_text
    
    def draw(self, canvas):
        if self.ui.keyboard_focus == self:
            canvas.set_color(self.style.accent)
        else:
            canvas.set_color(self.style.border)
        canvas.sketch_rectangle(0, 0, self.w, self.h)
        canvas.set_color(self.style.fg)
        canvas.paint_rectangle(1, 1, self.w-2, self.h-2)

        if self.enabled:
            if self.mouse_hover:
                canvas.set_color(self.style.highlight)
                canvas.paint_rectangle(1, 1, self.w-2, self.h-2)
        else:
            canvas.set_color(self.style.shadow)
            canvas.paint_rectangle(1, 1, self.w-2, self.h-2)

        self._text.paint(canvas, 4, self.h/2, alignment = "center_left")

    def mouse_pressed(self, x, y, button):
        pass

    def mouse_released(self, x, y, button):
        if self.mouse_hover:
            self.ui.acquire_keyboard(self)

    def key_pressed(self, key):
        if not self.enabled:
            return

        if key == sdl2.SDLK_RETURN:
            self.ui.release_keyboard()
        elif key == sdl2.SDLK_BACKSPACE:
            if len(self._text.text) > 0:
                self._text.text = self._text.text[:-1]

    def text_input(self, text):
        if not self.enabled:
            return

        self._text.text = self._text.text + text

class Label(Element):
    def __init__(self, ui, text = None, *args, **kvargs):
        super().__init__(ui, *args, **kvargs)

        self._text = draw.Text(canvas = ui.canvas, font = ui.font, text = "")
        if text is not None:
            self._text.text = text

    @property
    def text(self):
        return self._text.text
    
    @text.setter
    def text(self, new_text):
        self._text.text = new_text

    def draw(self, canvas):
        canvas.set_color(self.style.text)
        self._text.paint(canvas, 2, self.h/2, alignment="center_left")

class SimpleLayout(Element):
    def __init__(self, ui, style=None, parent=None):
        super().__init__(ui, style, parent)
        self.padding = 4
        self.direction = "vertical"
        

    def cleanUp(self):
        super().cleanUp()
        self.x = self.parent.padding.left
        self.y = self.parent.padding.top
        self.w = self.parent.w - self.parent.padding.left - self.parent.padding.right
        self.h = self.parent.h - self.parent.padding.top - self.parent.padding.bottom

        if self.direction == "vertical":
            coord = 'y'
            anchor = 'x'
            dimension = 'h'
            fill = 'w'
        elif self.direction == "horizontal":
            coord = 'x'
            anchor = 'y'
            dimension = 'w'
            fill = 'h'

        current = 0
        for ch in self.children:
            setattr(ch, fill, getattr(self, fill))
            setattr(ch, anchor, 0)
            setattr(ch, coord, current)
            current += getattr(ch, dimension) + self.padding

class FormLayout(Element):
    def __init__(self, *args, **kvargs):
        super().__init__(*args, **kvargs)
        self.rows = []
        self.padding = 4

    def addRow(self, row):
        self.rows.append(row)

    def cleanUp(self):
        super().cleanUp()

        y = self.padding
        for primary, secondary in self.rows:
            primary.x = self.padding
            primary.y = y
            
            secondary.x = primary.w + self.padding
            secondary.y = y
            secondary.w = self.w - secondary.x - self.padding
            secondary.h = primary.h

            y += primary.h + self.padding