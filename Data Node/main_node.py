from threading import Thread
from handler import *

if __name__ == "__main__":
    for i in range(len(node_ports)):
        p = Thread(target = handler.run(i))
        p.start()
        p.join()