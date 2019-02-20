"""
    Provides Engine which is a central point of the application.

    It is responsible for initializing the underlying backend library
    (SDL2) and allows for creating a window and managing the current state.
"""

from sdl2 import *
from sdl2.sdlimage import *
from sdl2.sdlttf import *

class Engine:
    """
    An engine which manages the application's screen and forwards the
    necessary events to the currently set `State`.
    """

    MOUSE_BUTTON_LOOKUP = {
        SDL_BUTTON_LEFT: "left",
        SDL_BUTTON_RIGHT: "right",
        SDL_BUTTON_MIDDLE: "middle",
        SDL_BUTTON_X1: "x1",
        SDL_BUTTON_X2: "x2"
    }

    def __init__(self):
        self.window = None
        self.renderer = None

    def create_window(self, title,
                           width,
                           height, 
                           x = SDL_WINDOWPOS_UNDEFINED,
                           y = SDL_WINDOWPOS_UNDEFINED):
        """
        Creates a window with the provided parameters.
        It also creates the renderer which is then accessible by
        `get_renderer` method.
        """
        self.window = SDL_CreateWindow(title.encode(), x, y, width, height, SDL_WINDOW_SHOWN | SDL_WINDOW_RESIZABLE)

        self.renderer = SDL_CreateRenderer(self.window, 0, 0)
        self.state = None
        self.target_frametime = 1.0/60.0

        SDL_SetRenderDrawBlendMode(self.renderer, SDL_BLENDMODE_BLEND);

    def new_state(self, state_class : "class derived from State"):
        """
        Alters the current state to be of the provided class.

        The class will be instantinated with the Engine as the only argument
        """
        self.state = state_class(self)

        return self.state

    def get_renderer(self):
        """
        Returns the current `SDL_Renderer`, can be used to wrap it up in a 
        `Canvas`
        """
        return self.renderer

    def set_target_frametime(self, seconds):
        self.target_frametime = seconds

    def loop(self):
        """
        Runs the engine's main loop. Should be always called at the end of
        window and state set-up.

        It handles the updating, drawing and event passing for the current
        `State`.
        """
        run = True
        ev = SDL_Event()
        while run:
            while SDL_PollEvent(ev) != 0:
                if ev.type == SDL_WINDOWEVENT:
                    if ev.window.event == SDL_WINDOWEVENT_CLOSE:
                        run = False

                elif ev.type == SDL_MOUSEBUTTONDOWN:
                    
                    self.state.mouse_pressed(
                        x = ev.button.x,
                        y = ev.button.y,
                        button = Engine.MOUSE_BUTTON_LOOKUP.get(ev.button.button, "?")
                    )

                elif ev.type == SDL_MOUSEBUTTONUP:
                    self.state.mouse_released(
                        x = ev.button.x,
                        y = ev.button.y,
                        button = Engine.MOUSE_BUTTON_LOOKUP.get(ev.button.button, "?")
                    )

                elif ev.type == SDL_KEYDOWN:
                    self.state.key_pressed(key = ev.key.keysym.sym)

                elif ev.type == SDL_KEYUP:
                    self.state.key_released(key = ev.key.keysym.sym)

                elif ev.type == SDL_TEXTINPUT:
                    self.state.text_input(bytes(ev.text.text).decode('utf8'))

            self.state.update(self.target_frametime)

            SDL_SetRenderDrawColor(self.renderer, 255, 255, 255, 255)
            SDL_RenderClear(self.renderer)
            self.state.draw()
            SDL_RenderPresent(self.renderer)

            SDL_Delay(1000//30);

    def __enter__(self):
        assert(SDL_Init(SDL_INIT_EVENTS
                        | SDL_INIT_VIDEO
                        | SDL_INIT_TIMER)
                == 0)

        assert(IMG_Init(IMG_INIT_PNG) != 0)
        assert(TTF_Init() == 0)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.renderer is not None:
            SDL_DestroyRenderer(self.renderer)
        if self.window is not None:
            SDL_DestroyWindow(self.window)
        
        TTF_Quit()
        IMG_Quit()
        SDL_Quit()

    def start_text_input(self):
        if SDL_IsTextInputActive() == False:
            SDL_StartTextInput()

    def stop_text_input(self):
        SDL_StopTextInput()

    def window_size(self):
        """
        Returns the current window's size in pixels.
        """
        w = c_int(-1)
        h = c_int(-1)

        SDL_GetWindowSize(self.window, w, h)

        return w.value, h.value

    def mouse_position(self):
        """
        Returns the current mouse position of the window.
        -1 for both coordinates if the mouse is outside

        The value returned is a tuple: `(x, y)`
        """
        x = c_int(-1)
        y = c_int(-1)

        SDL_GetMouseState(x, y)
       
        return (x.value, y.value)