from node_data import node_data
from user_data import user_data


class lookup(object):
    def __init__(self):
        self.nodes_data = []
        self.users_data = []

    def addNode(self, node):
        self.nodes_data.append()

    def drop_node(self, node):
        node.down_node()

    def filter(self):
        IPs = []
        for node in self.nodes_data:
            if node.alive == False:
                IPs.append(node.nodeIP)
        for nodeIP in IPs:
            for user in self.users_data:
                user.filterVideos(nodeIP)
            removed = []
            for node in self.nodes_data:
                if node.nodeIP == nodeIP:
                    removed.append(node)
            for node in removed:
                self.nodes_data.remove(node)
            print(f"Videos Removed From The Datakeeper which ip is:{nodeIP}")
