from libraries import *


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


def download(username, filename):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://{MASTER_TRACKER_IP}:{MASTER_CLIENT_REP}")
    msg = message(DOWNLOAD_REQUEST, f"{username} {filename}")

    # sending message to master tracker
    socket.send_pyobj(msg)
    print(f"Sending {DOWNLOAD_REQUEST} to master tracker")
    node_ips, node_ip_port, file_size = socket.recv_pyobj().message_content
    print(f"Got {node_ips} IPs and {node_ip_port} Ports, file_size: {file_size} bytes")

    context = zmq.Context()
    download_socket = context.socket(zmq.REQ)
    download_socket.connect(f"tcp://{node_ips}:{node_ip_port}")

    download_list_size = int(ceil(file_size / CHUNK_SIZE))
    downloaded_video = [bytearray(0)] * download_list_size

    for i in range(download_list_size):
        msg = message(DOWNLOAD_PROCESS, [i, username, filename])
        download_socket.send_pyobj(msg)
        [chunk, data] = download_socket.recv_pyobj().message_content
        downloaded_video[chunk] = data

    print(VIDEO_DONE)
    with open(f"{filename}", "wb") as file:
        for data in downloaded_video:
            file.write(data)


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
            filename = input("Enter video name please: ")
            download(username, filename)
        else:
            exit()


if __name__ == "__main__":
    main()
