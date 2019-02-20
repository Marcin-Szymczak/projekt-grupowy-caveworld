from shared.engine import Engine
from server.main import Main

import sys

with Engine() as e:
    e.create_window("Cave World - server", 1024, 768)
    s = e.new_state(Main)

    address = "localhost"
    port = 5505

    if len(sys.argv) > 1:
        address = sys.argv[1]
    
    if len(sys.argv) > 2:
        port = int(sys.argv[2])

    print("Serving on ", address, ":", port)

    s.host(address, port)

    e.loop()