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
    if node_ip is None:
        print("node keepers are down")
        return
    sender.connect(f"tcp://{node_ip}:{node_port}")

    f = Path(filename)
    if not f.exists():
        print("File does not exist")
        return

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


def download_threaded(username, filename, node_ip, node_port, downloaded_video, chunk, chunk_size):
    context = zmq.Context()
    download_socket = context.socket(zmq.REQ)
    download_socket.connect(f"tcp://{node_ip}:{node_port}")
    msg = message(DOWNLOAD_PROCESS, [chunk, username, filename, chunk_size])
    download_socket.send_pyobj(msg)
    [chunk, data] = download_socket.recv_pyobj().message_content
    downloaded_video[chunk] = data


def get_download_ip_port(list_ip_with_ports, visited):
    for i in range(len(list_ip_with_ports)):
        if not visited[i]:
            return list_ip_with_ports[i][0], list_ip_with_ports[i][1]

    shuffle(list_ip_with_ports)
    return list_ip_with_ports[0][0], list_ip_with_ports[0][1]


def download(username, filename):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://{MASTER_TRACKER_IP}:{MASTER_CLIENT_REP}")
    msg = message(DOWNLOAD_REQUEST, f"{username} {filename}")

    # sending message to master tracker
    socket.send_pyobj(msg)
    print(f"Sending {DOWNLOAD_REQUEST} to master tracker")
    list_ip_with_ports, file_size = socket.recv_pyobj().message_content
    print(f"Got {list_ip_with_ports}")

    if list_ip_with_ports is None:
        print(f"No file with this name belongs to you in the database")
        return
    if len(list_ip_with_ports) == 0:
        print(f"Sorry for that but the servers are down")
        return
    download_threads = []
    download_list_size = min(6, len(list_ip_with_ports))
    downloaded_video = [bytearray(0)] * download_list_size
    visited = [False] * len(list_ip_with_ports)
    for i in range(download_list_size):
        node_ip, node_port = get_download_ip_port(list_ip_with_ports, visited)
        download_threads.append(
            Thread(target=download_threaded,
                   args=(username, filename, node_ip,
                         node_port, downloaded_video, i, ceil(file_size / download_list_size))))

    for thread in download_threads:
        thread.start()

    for thread in download_threads:
        thread.join()

    print(VIDEO_DONE)
    with open(f"{filename}", "wb") as file:
        for data in downloaded_video:
            file.write(data)


def main():
    username = input("Enter your username please: ")
    while True:
        try:
            action = int(input("Enter an action:\n1:Upload\n2:Show files\n3:Download\n4:Exit\n"))
        except:
            print("please select correctly")
            continue
        if action == 1:
            filename = input("Enter video name please: ")
            upload(username, filename)
        elif action == 2:
            show_files(username)
        elif action == 3:
            filename = input("Enter video name please: ")
            download(username, filename)
        else:
            print("no option selected we have to close ^)^))^$")
            exit()


if __name__ == "__main__":
    main()
