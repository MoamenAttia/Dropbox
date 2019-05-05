class video(object):
    def __init__(self, filename, nodes, file_size):
        self.filename = filename
        self.nodes = nodes
        self.file_size = file_size

    def printVideo(self):
        print(f"video filename:{self.filename} video IPs")
        for node in self.nodes:
            print(f"node_ip: {node.node.nodeIP},node_ports: {node.node.nodePorts}")
