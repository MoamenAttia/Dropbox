from message import message
from constants import *
import zmq
import socket

# master_tracker as server to get requests from users.


def master_tracker_clinet():
    pass


# master_tracker as subscriber.
def master_tracker_subsciber():
    pass


# node_keeper sends success to update the lookup table.
def master_tracker_node_keeper():
    pass


def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://{MASTER_TRACKER_IP}:{MASTER_CLIENT_REP}")
    while True:
        try:
            msg = socket.recv_pyobj()
            print(msg.message_type)
            if msg.message_type == UPLOAD_REQUEST:
                # To be edited must send node ip
                msg = message(UPLOAD_REQUEST, [
                              master_tracker_ip, "3000"], master_tracker_ip, master_tracker_ports[0])
                socket.send_pyobj(msg)
                print(f"port:3000 sent")
        except:
            print("ERROR OCCURED")


if __name__ == "__main__":
    main()
