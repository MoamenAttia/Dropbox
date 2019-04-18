import zmq


def run(ip, port, filename):
    
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect (f"tcp://{ip}:{port}")

    file = open(filename, "wb")
    while True :
        data = socket.send_pyobj()
        socket.send_string("ok")
        if (data == "done"):
            break
        file.write(data)

    file.close()