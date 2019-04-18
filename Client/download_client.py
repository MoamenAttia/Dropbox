import zmq
from threading import Thread

class download:
    def __init__(self, userId, filename):
        self.video = []
        self.downloaded_video = []
        self.ack = "ok"
        self.userId = userId
        self.filename = filename
    
    def downloadProcess(self, ip, port, node, total, filename):
        context = zmq.Context()
    	socket = context.socket(zmq.REQ)
    	socket.connect (f"tcp://{ip}:{port}")
        
    	socket.send_string("download " + filename)
		self.ack = socket.recv_string()

        msg = f"{node},{total}"
        socket.send_string(msg)
        numSrc = int(socket.recv_string())
    	socket.send_string(self.ack)
		self.ack = socket.recv_string()

	   	thread_video = []
    	for i in range(numSrc):
			data = socket.recv_pyobj()
    		thread_video.append(data)
    		socket.send_string(self.ack)

    	self.ack = socket.recv_string()
    	self.video[node] = thread_video

    def run(self): 
		context = zmq.Context()
    	socket = context.socket(zmq.REQ)
    	socket.connect (f"tcp://{master_IP}:{master_ports}")

        req = str(self.userId + " download " + self.filename)
		socket.send_string(req)
        src = socket.recv_pyobj()

        processes = []
        total = len(src)

        for i in range(total):
    		thread = Thread(target = self.downloadProcess(src[i][0], src[i][1], i, total, filename))
    		processes.append(thread)

        for thread in processes:
    		thread.start()

    	for thread in processes:
    		thread.join()
	
        self.downloaded_video = []
    	for i in range(len(self.video)): 
    		self.downloaded_video.append(self.video[i])
    	return self.downloaded_video