from node_data import node_data
from constants import *


class lookup(object):
    def __init__(self):
        self.users_data = []
        self.nodes_data = [
            node_data(NODE_KEEPER_IP_1, [NODE_KEEPER_CLIENT_REP_1, NODE_KEEPER_MASTER_PUB_1, NODE_KEEPER_MASTER_REQ_1]),
            node_data(NODE_KEEPER_IP_2, [NODE_KEEPER_CLIENT_REP_2, NODE_KEEPER_MASTER_PUB_2, NODE_KEEPER_MASTER_REQ_2]),
            node_data(NODE_KEEPER_IP_3, [NODE_KEEPER_CLIENT_REP_3, NODE_KEEPER_MASTER_PUB_3, NODE_KEEPER_MASTER_REQ_3]),
            node_data(NODE_KEEPER_IP_4, [NODE_KEEPER_CLIENT_REP_4, NODE_KEEPER_MASTER_PUB_4, NODE_KEEPER_MASTER_REQ_4]),
            node_data(NODE_KEEPER_IP_5, [NODE_KEEPER_CLIENT_REP_5, NODE_KEEPER_MASTER_PUB_5, NODE_KEEPER_MASTER_REQ_5])
        ]

    def printInfo(self):
        for user in self.users_data:
            print(f"username:{user.username}, videos")
            for video in user.videos:
                print(f"filename:{video.filename} nodeIPs:{video.node_ips}")
        for node in self.nodes_data:
            print(f"node_ip:{node.nodeIP}, alive:{node.alive} last_time:{node.last_time} node_ports:{node.nodePorts}")
            for video in node.videos:
                print(f"filename:{video.filename} nodeIPs:{video.node_ips}")
