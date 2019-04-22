from threading import Lock, Thread
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
    msg = message(UPLOAD_REQUEST, f"{username}")

    # sending message to master tracker
    socket.send_pyobj(msg)
    print("Sending UPLOAD_REQUEST to master tracker")
    node_ip, node_port = socket.recv_pyobj().message_content

    sender_context = zmq.Context()
    sender = sender_context.socket(zmq.REQ)
    sender.connect(f"tcp://{node_ip}:{node_port}")

    # send username , video filename.
    msg = message(VIDEO_NAME_REQUEST, [username, filename])
    sender.send_pyobj(msg)
    print(f"SENDING {VIDEO_NAME_REQUEST} to node_tracker port {node_port}")
    sender.recv_pyobj()  # Dummy Response

    with open(filename, "rb") as file:
        data = file.read(chunksize)
        print(data)
        i = 1
        while data:
            msg = message(VIDEO, [username, filename, data])
            print(f"sending {i} chunk")
            sender.send_pyobj(msg)
            sender.recv_pyobj()
            print(f"chunk {i} sent")
            data = file.read(chunksize)
            i += 1

    msg = message(VIDEO_DONE, [username, filename, node_ip, node_port])
    sender.send_pyobj(msg)
    response = sender.recv_pyobj()
    print("File Uploaded")


def show_files(username):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://{MASTER_TRACKER_IP}:{MASTER_CLIENT_REP}")
    msg = message(SHOW_FILES, f"{username}")
    # sending message to master tracker
    socket.send_pyobj(msg)
    print(f"Sending {SHOW_FILES} to master tracker")

    res = socket.recv_pyobj()
    if len(res.message_content) == 0:
        print("you don't have any video in our fascinating Database")
    else:
        for video_item in res.message_content:
            video_item.printVideo()


downloaded_video = []


#
# def run_download(username, filename, ip, port, chunk_idx, num_threads):
#     context = zmq.Context()
#     socket = context.socket(zmq.REQ)
#     socket.connect(f"tcp://{ip}:{port}")
#     msg = message(DOWNLOAD_REQUEST, [username, filename, chunk_idx, num_threads])
#     socket.send_pyobj(msg)
#     response = socket.recv_pyobj()
#
#     numSrc = response.message_content
#     msg = message(OK, OK)
#     socket.send_pyobj(msg)
#
#     th_video = []
#
#     for i in range():
#         vd = socket.recv_pyobj()
#         th_video.append(vd.message_content)
#         msg = message(OK, OK)
#         socket.send_pyobj(msg)
#
#     res = socket.recv_pyobj()
#     downloaded_video[chunk_idx] = th_video


def download(username, filename):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://{MASTER_TRACKER_IP}:{MASTER_CLIENT_REP}")
    msg = message(DOWNLOAD_REQUEST, f"{username} {filename}")

    # sending message to master tracker
    socket.send_pyobj(msg)
    print(f"Sending {DOWNLOAD_REQUEST} to master tracker")

    # node_ips, node_ip_port = socket.recv_pyobj().message_content
    #
    # threads = []
    # for i in range(len(node_ips)):
    #     threads.append(
    #         Thread(target=run_download, args=(username, filename, node_ips[i], node_ip_port[i], i, len(node_ips),)))
    #
    # for thread in threads:
    #     thread.start()
    # for thread in threads:
    #     thread.join()
    #
    # with open("A7oh.mp4", "wb") as file:
    #     for chunk in downloaded_video:
    #         file.write(chunk)


def main():
    username = input("Enter your username please: ")
    while True:
        action = input("Enter an action:\n1:Upload\n2:Showfiles\n3:Download\n4:Exit\n")
        if int(action) == 1:
            filename = input("Enter video name please: ")
            upload(username, filename)
        elif int(action) == 2:
            show_files(username)
        elif int(action) == 3:
            pass
        else:
            exit()


if __name__ == "__main__":
    main()
