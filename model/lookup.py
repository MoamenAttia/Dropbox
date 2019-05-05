from libraries import *


def json_default(ordered_dict):
    return ordered_dict.__dict__


class lookup(object):
    def __init__(self):
        self.users_data = []
        self.nodes_data = []

    def printInfo(self):
        for user in self.users_data:
            print(f"username:{user.username}, videos")
            for video in user.videos:
                print(f"filename: {video.filename} nodeIPs: {video.node_ips} file_size: {video.file_size}")
        for node in self.nodes_data:
            print(
                f"node_ip: {node.nodeIP}, alive: {node.alive} last_time: {node.last_time} node_ports: {node.nodePorts}")

    def __repr__(self):
        return json.dumps(self, default=json_default, indent=4)
