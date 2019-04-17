import zmq
from lookup import *
from threading import Thread

def handler(port):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{port}")

    while True:
        req = socket.recv_string().split()   #req = userId action filename
        if (req[1] == "upload"):
            rep = upload_handler()
            socket.send_string(rep)
        elif (req[1] == "showfiles"):
            rep = showfiles_handler(req[0])
            socket.send_pyobj(rep)
        elif (req[1] == "download"):
            rep = download_handler(req[0], req[2])
            socket.send_pyobj(rep)
        
def showfiles_handler(userId):
    #search in lookup table with userId to get array of files
    return files

def upload_handler():
    #get an available node port  
    return f"{node_ip}, {node_port}"

def download_handler(userId, filename):
    #search in lookup table for filename and userid if we found it get the ports list and ip  
    return src # array [[ip, port]]

if __name__ == '__main__':
    processes = []
    for i in range(len(master_ports)):
    	thread = Thread(target = handler(port))
    	processes.append(thread)

    for thread in processes:
    	thread.start()

    for thread in processes:
    	thread.join()