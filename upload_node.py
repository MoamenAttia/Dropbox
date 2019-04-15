import zmq

class upload:    
    def __init__(self, port):
    	self.port = port
        self.ack

    def run(self, path):
        context = zmq.Context()
    	socket = context.socket(zmq.REP)
    	socket.bind("tcp://*:%s" % self.port)

    	video = read_file(path)
        size = len(video)

    	params = socket.recv_string()
    	params = params.split(",")
    	index = int(params[0]) #index of current node
    	total = int(params[1]) #total number of nodes taht will  send the file

        data = int(size/total)
        print(data)
        if (index == total - 1):
            add = data + size % total
        else:
            add = data

    	socket.send_string(str(numberOfChunks))
    	self.ack = socket.recv_string()

    	for i in range(index*data, index*data + add):
    	    socket.send_pyobj(video[i])
    	    ack = socket.recv_string()

    	socket.send_string(ack)