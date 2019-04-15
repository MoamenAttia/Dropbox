import zmq

class showfiles:
    def __init__(self):
        files = []

    def show(self, user_id):
        context = zmq.Context()
    	socket = context.socket(zmq.REQ)
    	socket.connect (f"tcp://{master_IP}:{master_ports}")
        msg = "showfiles ," + user_id
        socket.send_string(msg)
        files = socket.recv_string() # recieve array of filenames
        print("your files are: ")
        for i in range(len(files)):
            print(files[i] + '\n')
