from shared.engine import Engine
from client.main import Main
import sys, os

with Engine() as e:
    e.create_window("Cave World - client", 1024, 768)
    c = e.new_state(Main)
    
    address = "localhost"
    port = 5505

    if len(sys.argv) > 1:
        address = sys.argv[1]
    
    if len(sys.argv) > 2:
        port = int(sys.argv[2])

    print("Connecting to", address, ":", port)


    c.connect(address, port)

    e.loop()