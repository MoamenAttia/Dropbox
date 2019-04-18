import zmq

chunksize = 1000

def Upload(ip, port, filename, path):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect (f"tcp://{ip}:{port}")
  
    file = open(filepath, "rb")
    data = file.read(chunksize)
    while data:
        socket.send_pyobj(data)
        ack = socket.recv_string()
        data = file.read(chunksize)
    file.close()

    socket.send_string("done")
    ack = socket.recv_string()

def run(userId, filename, path):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect (f"tcp://{master_IP}:{master_ports}")

    req = userId + "upload"
    socket.send_string(req)
    rec = socket.recv_string().split()
    node_port = f"tcp://{rec[0]}:{rec[1]}"
    
    socket = context.socket(zmq.REQ)
    socket.connect(node_port)

    socket.send_string(userId + " upload " + fileName)
    ack = socket.recv_string()

    socket.send_string(client_Ip + client_port)
    ack = socket.recv_string()

    Upload(clientUploadIpPort, fileName)

