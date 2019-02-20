from shared.net.cave_world_protocol import actor

class TurnManager:
    def __init__(self, main):
        self.actors = []
        self.client_actors = {}

        self.turn_index = -1

        self.network = main.network

        self.network.bind({
            actor.TurnRequest: self.on_turn_request
        })
    
    def current_turn(self):
        if self.turn_index == -1:
            return None
        return self.actors[self.turn_index]
    
    def next_turn(self):
        self.turn_index = (self.turn_index + 1) % len(self.actors)
        a = self.current_turn()

        turn_request = actor.PrepareTurnRequest({
            "actor": {
                "type": a.representation(),
                "x": a.x,
                "y": a.y,

                "senses": a.gather_senses_information(),
                "condition": {
                    "hunger": 0.0,
                    "thirst": 0.0,
                    "temperature": 0.0,
                    "health": 100.0
                }
            }
        })
        self.network.send_to(self.current_turn().client, turn_request)

    def register_actor(self, actor):
        self.actors.append(actor)
        self.client_actors[actor.client] = actor

        if len(self.actors) == 1:
            self.next_turn()

    def unregister_client(self, client):
        actor = self.client_actors[client]
        del self.client_actors[client]
        self.actors.remove(actor)

        if len(self.actors) == 0:
            self.turn_index = -1

        return actor

    def on_turn_request(self, message, client):
        current = self.current_turn()
        if not current or current.client != client:
            self.network.send(client, actor.TurnResult({
                "success": False,
                "error": "Other client's turn is in progress"
            }))