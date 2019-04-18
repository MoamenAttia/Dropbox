import zmq
import time
from threading import Thread
from alive_master import receive_alive
from client_handler import handler
from node_handler import *

if __name__ == "__main__":
    
    clientProcesses = []  
    alive = Thread(target = receive_alive(port)) # a port dedicated to receive alive msg?

    for i in range(len(master_ports)):
        thread = Thread(target = handler(i)) # should i pass the alive nodes ?
    	clientProcesses.append(thread)

    alive.start()
    for thread in clientProcesses:
        thread.start()
    
    alive.join()
    for thread in clientProcesses:
        thread.join()