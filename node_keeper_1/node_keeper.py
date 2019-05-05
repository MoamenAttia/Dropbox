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


def replicate(node_ip, node_port, username, filename):
    sender_context = zmq.Context()
    sender = sender_context.socket(zmq.REQ)
    sender.connect(f"tcp://{node_ip}:{node_port}")
    print(filename)
    # send username , video filename.
    msg = message(VIDEO_NAME_REQUEST, [username, filename])
    sender.send_pyobj(msg)
    print(f"SENDING {VIDEO_NAME_REQUEST} to node_tracker port {node_port} with data {msg.message_content}")
    sender.recv_pyobj()  # Dummy Response

    username_filename = f"{username}_{filename}"
    with open(username_filename, "rb") as file:
        file_size = os.path.getsize(username_filename)
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
    exit(0)


def handle_message(msg, success_socket):
    if msg.message_type == VIDEO_NAME_REQUEST:
        print(f"I am receiving request {VIDEO_NAME_REQUEST} request")
        create_file(msg)
        return message(OK, OK)
    elif msg.message_type == VIDEO:
        print(f"I am receiving request {VIDEO} request")
        append_file(msg)
        return message(OK, OK)
    elif msg.message_type == VIDEO_DONE:
        print(f"I am receiving request {VIDEO_DONE} request")
        new_msg = message(UPLOAD_SUCCESS, msg.message_content)
        print(f"I am sending {UPLOAD_SUCCESS} request to master tracker")
        success_socket.send_pyobj(new_msg)
        response = success_socket.recv_pyobj()
        print(f"{UPLOAD_SUCCESS} sent {response.message_type}")
        return message(OK, OK)
    elif msg.message_type == DOWNLOAD_PROCESS:
        print(f"I am receiving request {DOWNLOAD_PROCESS} request")
        chunk, username, filename = msg.message_content
        data = read_chunk(chunk, username, filename)
        return message(DOWNLOAD_PROCESS, [chunk, data])
    elif msg.message_type == REPLICATION_REQUEST:
        print(f"I am receiving request {REPLICATION_REQUEST} request")
        ip_ports = msg.message_content[0]
        username = msg.message_content[1]
        filename = msg.message_content[2]
        print(f"I received {ip_ports} , {filename}")
        for ip_port in ip_ports:
            Thread(target=replicate, args=(ip_port[0], ip_port[1], username, filename,)).start()
        return message(OK, OK)


def node_keeper_publisher(node_keeper_ip, node_keeper_port):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(f"tcp://*:{node_keeper_port}")
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
        print(f"{reply.message_type} sent back")
        socket.send_pyobj(reply)


def welcome(node_ip, node_ports):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://{MASTER_TRACKER_IP}:{MASTER_WELCOME_PORT}")
    msg = message(NEW_NODE, [node_ip, node_ports])
    # sending message to master tracker
    socket.send_pyobj(msg)
    print(f"Sending {NEW_NODE} to master tracker")
    res = socket.recv_pyobj()
    print(res.message_type)


def node_keeper_replicate(node_ip, node_port):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{node_port}")

    # Socket to send success message to master to update lookup table
    success_socket = zmq.Context().socket(zmq.REQ)
    success_socket.connect(f"tcp://{MASTER_TRACKER_IP}:{MASTER_NODE_KEEPER_REP}")

    while True:
        msg = socket.recv_pyobj()
        reply = handle_message(msg, success_socket)
        print(f"{reply.message_type} sent back")
        socket.send_pyobj(reply)


def main():
    node_ip = NODE_KEEPER_IP_1
    download_ports = ["5000", "5002", "5004"]
    replicate_ports = ["5100", "5102", "5104"]
    upload_ports = ["5200", "5202", "5204"]
    publisher_port = "5300"
    node_ports = download_ports + replicate_ports + [publisher_port] + upload_ports
    print(f"node ip:{node_ip}, node ports:{node_ports}")
    welcome(node_ip, node_ports)
    print("node keeper added to the lookup table")
    for port in download_ports:
        Thread(target=node_keeper_client, args=(node_ip, port,)).start()

    for port in upload_ports:
        Thread(target=node_keeper_client, args=(node_ip, port,)).start()

    for port in replicate_ports:
        Thread(target=node_keeper_replicate, args=(node_ip, port,)).start()

    Thread(target=node_keeper_publisher, args=(node_ip, publisher_port,)).start()


if __name__ == "__main__":
    main()
