class node_data(object):
    def __init__(self, node_ip, node_ports):
        self.alive = False
        self.nodePorts = node_ports
        self.nodeIP = node_ip
        self.last_time = 0
