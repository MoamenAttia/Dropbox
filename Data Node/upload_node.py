import zmq

class upload:    
    def __init__(self, port):
    	self.port = port
        self.ack = "ok"

    def run(self):
        context = zmq.Context()
    	socket = context.socket(zmq.REP)
    	socket.bind(f"tcp://*:{self.port}")

    	video = socket.recv_string()
		socket.send_string(self.ack)

		params = socket.recv_string()
		socket.send_string(self.ack)
    	params = params.split(",")
    	index = int(params[0]) #index of current node
    	total = int(params[1]) #total number of nodes taht will  send the file

        size = len(video)
        data = int(size/total)
        
		if (index == total - 1):
            add = data + size % total
        else:
            add = data
        chunk = str(add) 
    	socket.send_string(chunk)
    	self.ack = socket.recv_string()

    	for i in range(index*data, index*data + add):
    	    socket.send_pyobj(video[i])
    	    self.ack = socket.recv_string()

    	socket.send_string(self.ack)