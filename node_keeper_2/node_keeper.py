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
    with open(f"{username}_{filename}", "ab") as file:
        file.write(data)


def replicate(node_ip, node_port, filename):
    sender_context = zmq.Context()
    sender = sender_context.socket(zmq.REQ)
    sender.connect(f"tcp://{node_ip}:{node_port}")
    A7A = filename.split("_")
    print(A7A)

    username, filename = filename.split("_")
    print(username, filename)
    # send username , video filename.
    msg = message(VIDEO_NAME_REQUEST, [username, filename])
    sender.send_pyobj(msg)
    print(f"SENDING {VIDEO_NAME_REQUEST} to node_tracker port {node_port} with data {msg.message_content}")
    sender.recv_pyobj()  # Dummy Response

    filename = f"{username}_{filename}"
    with open(filename, "rb") as file:
        file_size = os.path.getsize(filename)
        print(file_size)
        data = file.read(CHUNK_SIZE)
        i = 1
        while data:
            msg = message(VIDEO, [username, filename, data])
            print(f"sending {i} chunk")
            sender.send_pyobj(msg)
            sender.recv_pyobj()
            print(f"chunk {i} sent")
            data = file.read(CHUNK_SIZE)
            i += 1

    msg = message(VIDEO_DONE, [username, filename, node_ip, node_port, file_size])
    sender.send_pyobj(msg)
    response = sender.recv_pyobj()
    print("File Uploaded")


def handle_message(msg, success_socket):
    print("Iam Receiving now", msg.message_type)
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
    elif msg.message_type == REPLICATION_REQUEST:
        ip_ports = msg.message_content[0]
        filename = msg.message_content[1]
        for ip_port in ip_ports:
            Thread(target=replicate, args=(ip_port[0], ip_port[1], filename,)).start()

        return message(OK, OK)


def node_keeper_publisher(node_keeper_ip, node_keeper_port):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(f"tcp://*:{node_keeper_port}")
    print(f"{node_keeper_ip}, {node_keeper_port}")
    filter_top = "10000"
    while True:
        socket.send_string(f"{filter_top} {node_keeper_ip} {node_keeper_port}")
        sleep(1)


def node_keeper_client(node_ip, node_port):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{node_port}")

    # Socket to send success message to master to update lookup table
    success_socket = zmq.Context().socket(zmq.REQ)
    success_socket.connect(f"tcp://{MASTER_TRACKER_IP}:{MASTER_NODE_KEEPER_REP}")

    while True:
        msg = socket.recv_pyobj()
        reply = handle_message(msg, success_socket)
        socket.send_pyobj(reply)


def main():
    Thread(target=node_keeper_client, args=(NODE_KEEPER_IP_2, NODE_KEEPER_CLIENT_REP_2,)).start()
    Thread(target=node_keeper_publisher, args=(NODE_KEEPER_IP_2, NODE_KEEPER_MASTER_PUB_2,)).start()


if __name__ == "__main__":
    main()
