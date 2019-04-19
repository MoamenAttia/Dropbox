class lookup(object):
    def __init__(self):
        self.nodes_data = []
        self.users_data = []

    def drop_node(self, node):
        node.down_node()