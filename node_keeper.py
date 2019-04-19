import zmq
from message import *
import socket
from time import sleep

node_ip = socket.gethostbyname(socket.gethostname())
node_ports = ["3000", "3100", "3200"]


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
    socket.bind(f"tcp://{node_ip}:{port}")
    while True:
        msg = message(ALIVE, ALIVE, node_ip, port)
        print("I AM ALIVE")
        socket.send_pyobj(msg)
        sleep(1)


def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://{node_ip}:{node_ports[0]}")
    while True:
        msg = socket.recv_pyobj()
        print(msg.message_type)
        handle_message(msg)
        socket.send_pyobj(message(OK, OK, node_ip, node_ports[0]))
        print("OK sent")


if __name__ == "__main__":
    main()
