"""
Provides abstract class of current application's state.
"""

from abc import ABC, abstractmethod

class State(ABC):
    """
    Abstract base class for all the application's states.

    The `State` class is provided to the `Engine` method `new_state` to set the
    active state to a new one instantinated with the provided implementation.

    Current state receives update and draw method calls and all of the user
    interaction events: `key_pressed`, `key_released`, `mouse_pressed`, `mouse_released`
    """
    def __init__(self):
        pass

    @abstractmethod 
    def update(self, dt):
        """
        Called whenever the state should be updated, as fast as possible.
        Typically every 16.666 ms (60 FPS), but can be different than that.
        This means that every time-based property should be properly integrated,
        for example by doing:
            ```
            position += speed * dt
            ```
        instead of
            ```
            position += speed
            ```
        """
        pass
    
    @abstractmethod
    def draw(self):
        """
        Called whenever the state should be drawn.
        Typically should NOT mutate the State's state, because there is no
        information about how much time passed between each draws. It is
        recommended to alter the state in the `update` method and use the
        `draw` method to only present the current results.
        """
        pass

    @abstractmethod
    def key_pressed(self, key):
        """
        Called whenever a key on the keyboard is pressed, with the key information
        as SDL_KeySym
        """
        pass

    @abstractmethod
    def key_released(self, key):
        """
        Same as the `key_pressed` but for the release event.
        """
        pass

    @abstractmethod
    def mouse_pressed(self, x, y, button):
        """
        Called whenever a mouse key is pressed. The x, y are the screen coordinates
        of the click.

        `button` is a string and it can be:
        - `left`
        - `right`
        - `middle`
        - `x1`
        - `x2`
        """
        pass
    
    @abstractmethod
    def mouse_released(self, x, y, button):
        """
        Same as `mouse_pressed` but for the release event.
        """
        pass
