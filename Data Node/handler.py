import zmq
from upload_node import *
from download_node import *

def run(port):
    while True:
        req = socket.recv_string().split()
        socket.send_string("ok")

        if (req[0] == "upload"):
        elif (req[0] == "download"):
            up = upload_node(port, req[1])
            up.run()
    