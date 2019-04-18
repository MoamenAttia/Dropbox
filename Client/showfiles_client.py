import zmq

class showfiles:
    def __init__(self):
        self.files = []

    def run(self, user_id):
        context = zmq.Context()
    	socket = context.socket(zmq.REQ)
    	socket.connect (f"tcp://{master_IP}:{master_ports}")
        
        msg = userId + " showfiles"
        socket.send_string(msg)
        self.files = socket.recv_pyobj()
        
        print("your files are: ")
        for i in range(len(self.files)):
            print(self.files[i] + '\n')
