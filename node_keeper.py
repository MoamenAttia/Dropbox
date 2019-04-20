import zmq
from message import message
import socket
from time import sleep
from constants import *


def handle_message(msg):
    if msg.message_type == VIDEO_NAME_REQUEST:
        create_file(msg)
    elif msg.message_type == VIDEO:
        append_file(msg)


def create_file(msg):
    [username, filename] = msg.message_content
    file = open(f"{username}_{filename}", "wb")
    file.close()


def append_file(msg):
    [username, filename, data] = msg.message_content
    print(data)
    with open(f"{username}_{filename}", "ab") as file:
        file.write(data)


def publisher(port):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(f"tcp://{NODE_KEEPER_IP_1}:{NODE_KEEPER_MASTER_PUB_1}")
    while True:
        msg = message(ALIVE, ALIVE, NODE_KEEPER_IP_1, NODE_KEEPER_MASTER_PUB_1)
        print("I AM ALIVE")
        socket.send_pyobj(msg)
        sleep(1)


def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    
    socket.bind(f"tcp://{NODE_KEEPER_IP_1}:{NODE_KEEPER_CLIENT_REP_1}")
    while True:
        msg = socket.recv_pyobj()
        print(msg.message_type)
        handle_message(msg)
        socket.send_pyobj(message(OK, OK, NODE_KEEPER_IP_1, NODE_KEEPER_CLIENT_REP_1))
        print("OK sent")


if __name__ == "__main__":
    main()
