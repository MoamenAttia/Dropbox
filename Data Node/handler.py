import zmq
import threading as Thread
from upload_node import *
from download_node import *

def run(port):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{port}")

    while True:
        req = socket.recv_string().split()
        socket.send_string("ok")

        if (req[1] == "upload"):
            rec = socket.recv_string().split()
            fileName = req[2] + ',' + req[0]
            dw = Thread(target = download_node.run(ipPort, fileName))
            dw.start()
        elif (req[1] == "download"):
            up = upload_node(port, req[1])
            up.run() #make it thread
    