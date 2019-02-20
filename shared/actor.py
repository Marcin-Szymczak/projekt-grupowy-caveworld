class Condition:
    """
    Current needs of an actor.
    """
    def __init__(self):
        self.hunger = 0
        self.thirst = 0
        self.temperature = 0
        self.health = 0

class Actor:
    """
    Superclass of all actors
    """
    def __init__(self):
        self.x = None
        self.y = None

        self.condition = Condition()