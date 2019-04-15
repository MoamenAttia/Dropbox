import zmq
from threading import Thread

class download:
    def __init__(self):
        self.video = []
        self.downloaded_video = []
        self.ack = "ok"
    
    def downloadProcess(self, ip, port, node, total):
        context = zmq.Context()
    	socket = context.socket(zmq.REQ)
    	socket.connect (f"tcp://{ip}:{port}")
        
        msg = f"{node},{total}"
        socket.send_string(msg)
        numSrc = int(socket.recv_string())
    	socket.send_string(self.ack)
        
        self.video = []
    	for i in range(numSrc):
    		data = socket.recv_pyobj()
    		video.append(data)
    		socket.send_string(self.ack)

    	message = socket.recv_string()
    	self.video[nodeIndex] = video


    def run(self, src): # src = [ip, port]
        processes = []
        total = len(src)

        for i in range(nodes):
    		thread = Thread(target=self.downloadProcess(src[i][0], src[i][1], i, total))
    		processes.append(thread)

        for thread in processes:
    		thread.start()

    	for thread in processes:
    		thread.join()
	
        self.downloaded_video = []
    	for i in range(len(self.video)): ######
    		self.downloaded_video.append(self.video[i])
    	return self.downloaded_video