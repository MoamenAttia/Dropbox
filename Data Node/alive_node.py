import zmq
import sys
import time
import socket 

def getIP():
    hostname = socket.gethostname()    
    IPAddr = socket.gethostbyname(hostname)
    return IPAddr

def send_alive(node_id):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect(f"tcp://{master_IP}:{master_ports}" )

    node_ip = getIP()
    while True:
        socket.send_string(f"{node_id}, {node_ip}")
        time.sleep(1)