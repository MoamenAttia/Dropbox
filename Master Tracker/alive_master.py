import zmq
import time
import threading as Thread

def update():
# update lookup table

def receive_alive(port):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.bind (f"tcp://*:{port}")
	
    update = Thread(target = update()) 
    update.start()