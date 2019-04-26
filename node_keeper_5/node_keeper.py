from libraries import *


def read_chunk(chunk, username, filename):
    read_from = chunk * CHUNK_SIZE

    with open(f"{username}_{filename}", "rb") as file:
        file.seek(read_from, os.SEEK_SET)
        return file.read(CHUNK_SIZE)


def create_file(msg):
    [username, filename] = msg.message_content
    file = open(f"{username}_{filename}", "wb")
    file.close()


def append_file(msg):
    [username, filename, data] = msg.message_content
    print(data)
    with open(f"{username}_{filename}", "ab") as file:
        file.write(data)


def handle_message(msg, success_socket):
    if msg.message_type == VIDEO_NAME_REQUEST:
        create_file(msg)
        return message(OK, OK)
    elif msg.message_type == VIDEO:
        append_file(msg)
        return message(OK, OK)
    elif msg.message_type == VIDEO_DONE:
        new_msg = message(UPLOAD_SUCCESS, msg.message_content)
        success_socket.send_pyobj(new_msg)
        response = success_socket.recv_pyobj()
        print(response.message_type)
        return message(OK, OK)
    elif msg.message_type == DOWNLOAD_PROCESS:
        chunk, username, filename = msg.message_content
        data = read_chunk(chunk, username, filename)
        return message(DOWNLOAD_PROCESS, [chunk, data])


def node_keeper_publisher(node_keeper_ip, node_keeper_port):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(f"tcp://{node_keeper_ip}:{node_keeper_port}")
    print(f"{node_keeper_ip}, {node_keeper_port}")
    filter_top = "10000"
    while True:
        socket.send_string(f"{filter_top} {node_keeper_ip} {node_keeper_port}")
        sleep(1)


def node_keeper_client(node_ip, node_port):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://{node_ip}:{node_port}")

    # Socket to send success message to master to update lookup table
    success_socket = zmq.Context().socket(zmq.REQ)
    success_socket.connect(f"tcp://{MASTER_TRACKER_IP}:{MASTER_NODE_KEEPER_REP}")

    while True:
        msg = socket.recv_pyobj()
        reply = handle_message(msg, success_socket)
        socket.send_pyobj(reply)


def main():
    Thread(target=node_keeper_client, args=(NODE_KEEPER_IP_5, NODE_KEEPER_CLIENT_REP_5,)).start()
    Thread(target=node_keeper_publisher, args=(NODE_KEEPER_IP_5, NODE_KEEPER_MASTER_PUB_5,)).start()


if __name__ == "__main__":
    main()
