import zmq
from message import message
from constants import *
import socket

client_ip = socket.gethostbyname(socket.gethostname())
client_ports = ["2000", "2100"]

chunksize = 10000


def upload(username, filename):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://{MASTER_TRACKER_IP}:{MASTER_CLIENT_REP}")
    msg = message(UPLOAD_REQUEST, UPLOAD_REQUEST, client_ip, client_ports[0])

    # sending message to master tracker
    socket.send_pyobj(msg)
    print("Sending UPLOAD_REQUEST to master tracker")
    [node_ip, node_port] = socket.recv_pyobj().message_content

    senderContext = zmq.Context()
    sender = senderContext.socket(zmq.REQ)
    sender.connect(f"tcp://{node_ip}:{node_port}")

    # send username , video filename.
    msg = message(VIDEO_NAME_REQUEST, [username, filename], client_ip, client_ports[1])
    sender.send_pyobj(msg)
    print(f"SENDING {VIDEO_NAME_REQUEST} to node_tracker port {node_port}")
    response = sender.recv_pyobj()

    with open(filename, "rb") as file:
        data = file.read(chunksize)
        print(data)
        i = 1
        while data:
            msg = message(VIDEO, [username, filename, data], client_ip, client_ports[1])
            print(f"sending {i} chunk")
            sender.send_pyobj(msg)
            response = sender.recv_pyobj()
            print(f"chunk {i} sent")
            data = file.read(chunksize)
            i += 1

    msg = message(VIDEO_DONE, VIDEO_DONE, client_ip, client_ports[0])
    sender.send_pyobj(msg)
    response = sender.recv_pyobj()
    print("File Uploaded")


def main():
    username = input("Enter your username please: ")
    while True:
        action = input(
            "Enter an action:\n1:Upload\n2:Showfiles\n3:Download\n4:Exit\n")
        if (int(action) == 1):  # upload
            filename = input("Enter video name please: ")
            upload(username, filename)


if __name__ == "__main__":
    main()
