from lookup import lookup
from threading import Thread
from node_data import node_data
from message import message
from node_data import node
import zmq


DOWNLOAD = "DOWNLOAD"
UPLOAD = "UPLOAD"
ALIVE = "ALIVE"

node_tracker_ports = ["5000", "5002"]
lookup_table = lookup()


def filter():
    lookup_table.filter()


def handle_message(msg):
    if msg.message_type == DOWNLOAD:
        pass
    elif msg.message_type == UPLOAD:
        pass
    elif msg.message_type == ALIVE:
        pass


def tracker_server_to_client(tracker_port):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://localhost:%s" % tracker_port)
    while True:


def tracker_server_to_node_tracker(tracker_port):
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)  # Job Distributer
    socket.bind("tcp://localhost:%s" % tracker_port)
    while True:
        msg = socket.recv_pyobj()
        handle_message(msg)


def tracker_server_from_node_tracker(tracker_port):
    context = zmq.Context()
    receiver = context.socket(zmq.PULL)
    receiver.bind("tcp://localhost:%s" % tracker_port)
    while True:
        msg = receiver.recv_pyobj()
        handle_message(msg)


if __name__ == "__main__":
    tracker_ports_to_client = ["1000", "1002"]
    tracker_port_to_node_trackers = "1004"
    tracker_port_from_node_trackers = "1006"

    for port in tracker_ports_to_client:
        Thread(target=tracker_server_to_client, args=(port,)).start()
