from video import video


class node_data(object):
    def __init__(self, nodePorts, nodeIP):
        self.alive = True
        self.nodePorts = nodePorts
        self.nodeIP = nodeIP
        self.videos = []

    def down_node(self):
        self.alive = False