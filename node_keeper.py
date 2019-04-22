import zmq
from message import message
from time import sleep
from constants import *
from threading import Thread, Lock


#
# def readChunk(msg, download_socket):
#     username, filename, chunk_idx, num_threads = msg.message_content
#     fileData = None
#     with open(f"{username}_{filename}", "rb") as file:
#         fileData = file.read()
#     fileSize = len(fileData)
#     chunkData = fileSize / num_threads
#
#     if chunk_idx == num_threads - 1:
#         rem = chunkData + fileSize % num_threads
#     else:
#         rem = chunkData
#
#     msg = message(DOWNLOAD_PROCESS, chunkData)
#     download_socket.send_pyobj(msg)
#     res = download_socket.recv_pyobj()
#
#     for i in range(chunk_idx * chunkData, chunk_idx * chunkData + rem):
#         download_socket.send_pyobj(fileData[i])
#         res = download_socket.recv_pyobj()
#
#     msg = message(OK, OK)
#     download_socket.send_pyobj(msg)


def handle_message(msg, success_socket, download_socket):
    if msg.message_type == VIDEO_NAME_REQUEST:
        create_file(msg)
    elif msg.message_type == VIDEO:
        append_file(msg)
    elif msg.message_type == VIDEO_DONE:
        new_msg = message(UPLOAD_SUCCESS, msg.message_content)
        success_socket.send_pyobj(new_msg)
        response = success_socket.recv_pyobj()
        print("OK")
    # elif msg.message_type == DOWNLOAD_REQUEST:
    #     readChunk(msg, download_socket)


def create_file(msg):
    [username, filename] = msg.message_content
    file = open(f"{username}_{filename}", "wb")
    file.close()


def append_file(msg):
    [username, filename, data] = msg.message_content
    print(data)
    with open(f"{username}_{filename}", "ab") as file:
        file.write(data)


def node_keeper_publisher(node_keeper_ip, node_keeper_port):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(f"tcp://{node_keeper_ip}:{node_keeper_port}")
    print(f"{node_keeper_ip}, {node_keeper_port}")
    filter_top = "10000"
    while True:
        socket.send_string(f"{filter_top} {node_keeper_ip}")
        sleep(1)


def node_keeper_client(node_ip, node_port):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://{node_ip}:{node_port}")

    success_socket = zmq.Context().socket(zmq.REQ)
    success_socket.connect(f"tcp://{MASTER_TRACKER_IP}:{MASTER_NODE_KEEPER_REP}")

    while True:
        msg = socket.recv_pyobj()
        print(msg.message_type)
        handle_message(msg, success_socket, socket)
        socket.send_pyobj(message(OK, OK))
        print("OK sent")


def main():
    Thread(target=node_keeper_client, args=(NODE_KEEPER_IP_1, NODE_KEEPER_CLIENT_REP_1,)).start()
    Thread(target=node_keeper_client, args=(NODE_KEEPER_IP_2, NODE_KEEPER_CLIENT_REP_2,)).start()
    Thread(target=node_keeper_client, args=(NODE_KEEPER_IP_3, NODE_KEEPER_CLIENT_REP_3,)).start()
    Thread(target=node_keeper_client, args=(NODE_KEEPER_IP_4, NODE_KEEPER_CLIENT_REP_4,)).start()
    Thread(target=node_keeper_client, args=(NODE_KEEPER_IP_5, NODE_KEEPER_CLIENT_REP_5,)).start()

    Thread(target=node_keeper_publisher, args=(NODE_KEEPER_IP_1, NODE_KEEPER_MASTER_PUB_1,)).start()
    Thread(target=node_keeper_publisher, args=(NODE_KEEPER_IP_2, NODE_KEEPER_MASTER_PUB_2,)).start()
    Thread(target=node_keeper_publisher, args=(NODE_KEEPER_IP_3, NODE_KEEPER_MASTER_PUB_3,)).start()
    Thread(target=node_keeper_publisher, args=(NODE_KEEPER_IP_4, NODE_KEEPER_MASTER_PUB_4,)).start()
    Thread(target=node_keeper_publisher, args=(NODE_KEEPER_IP_5, NODE_KEEPER_MASTER_PUB_5,)).start()


if __name__ == "__main__":
    main()
