from libraries import *

lookup_table = lookup()
mutex = Lock()


def does_node_have_ip_have_port(node, node_ip, node_port):
    if node.nodeIP == node_ip and node_port in node.nodePorts:
        return True
    return False


def get_node_by_ip_port(node_ip, node_port):
    for node_keeper in lookup_table.nodes_data:
        if node_keeper.nodeIP == node_ip and node_port in node_keeper.nodePorts:
            return node_keeper


def is_alive(ip, port):
    for node_keeper in lookup_table.nodes_data:
        if node_keeper.nodeIP == ip and port in node_keeper.nodePorts:
            return node_keeper.alive
    return False


def get_video_by_user_file(username, filename):
    video_name = f"{username}_{filename}"
    for user in lookup_table.users_data:
        if user.username == username:
            for vid in user.videos:
                if vid.filename == video_name:
                    return vid


def get_download_ports_with_file_size(username, filename):
    mutex.acquire()
    video_to_be_searched = get_video_by_user_file(username, filename)
    list_ip_with_ports = []
    for node_keeper in video_to_be_searched.nodes:
        if is_alive(node_keeper.nodeIP, node_keeper.nodePorts[0]):
            if does_node_have_ip_have_port(node_keeper, NODE_KEEPER_IP_1, NODE_KEEPER_CLIENT_REP_1):
                list_ip_with_ports.append((NODE_KEEPER_IP_1, NODE_KEEPER_CLIENT_REP_1))
            elif does_node_have_ip_have_port(node_keeper, NODE_KEEPER_IP_2, NODE_KEEPER_CLIENT_REP_2):
                list_ip_with_ports.append((NODE_KEEPER_IP_2, NODE_KEEPER_CLIENT_REP_2))
            elif does_node_have_ip_have_port(node_keeper, NODE_KEEPER_IP_3, NODE_KEEPER_CLIENT_REP_3):
                list_ip_with_ports.append((NODE_KEEPER_IP_3, NODE_KEEPER_CLIENT_REP_3))
            elif does_node_have_ip_have_port(node_keeper, NODE_KEEPER_IP_4, NODE_KEEPER_CLIENT_REP_4):
                list_ip_with_ports.append((NODE_KEEPER_IP_4, NODE_KEEPER_CLIENT_REP_4))
            elif does_node_have_ip_have_port(node_keeper, NODE_KEEPER_IP_5, NODE_KEEPER_CLIENT_REP_5):
                list_ip_with_ports.append((NODE_KEEPER_IP_5, NODE_KEEPER_CLIENT_REP_5))
    mutex.release()
    return list_ip_with_ports, video_to_be_searched.file_size


def get_free_port():
    mutex.acquire()
    shuffle(lookup_table.nodes_data)
    for node_keeper in lookup_table.nodes_data:
        if node_keeper.alive:
            if does_node_have_ip_have_port(node_keeper, NODE_KEEPER_IP_1, NODE_KEEPER_CLIENT_REP_1):
                mutex.release()
                return [NODE_KEEPER_IP_1, NODE_KEEPER_CLIENT_REP_1]
            elif does_node_have_ip_have_port(node_keeper, NODE_KEEPER_IP_2, NODE_KEEPER_CLIENT_REP_2):
                mutex.release()
                return [NODE_KEEPER_IP_2, NODE_KEEPER_CLIENT_REP_2]
            elif does_node_have_ip_have_port(node_keeper, NODE_KEEPER_IP_3, NODE_KEEPER_CLIENT_REP_3):
                mutex.release()
                return [NODE_KEEPER_IP_3, NODE_KEEPER_CLIENT_REP_3]
            elif does_node_have_ip_have_port(node_keeper, NODE_KEEPER_IP_4, NODE_KEEPER_CLIENT_REP_4):
                mutex.release()
                return [NODE_KEEPER_IP_4, NODE_KEEPER_CLIENT_REP_4]
            elif does_node_have_ip_have_port(node_keeper, NODE_KEEPER_IP_5, NODE_KEEPER_CLIENT_REP_5):
                mutex.release()
                return [NODE_KEEPER_IP_5, NODE_KEEPER_CLIENT_REP_5]
    mutex.release()
    print("Returned NULL PORT")
    return [None, None]


def update_alive():
    while True:
        current_time = time()
        mutex.acquire()
        for node_keeper in lookup_table.nodes_data:
            if current_time - node_keeper.last_time <= 2:
                node_keeper.alive = True
            else:
                node_keeper.alive = False
        mutex.release()


def handle_message(msg):
    if msg.message_type == UPLOAD_REQUEST:
        flag = False
        for user in lookup_table.users_data:
            if user.username == msg.message_content:
                flag = True
                break
        if not flag:
            lookup_table.users_data.append(user_data(msg.message_content))
        # To be edited must send node ip
        [node_keeper_ip, node_keeper_port] = get_free_port()
        print(f"ip:{node_keeper_ip}, port:{node_keeper_port} SENT")
        return message(UPLOAD_REQUEST, [node_keeper_ip, node_keeper_port])
    elif msg.message_type == SHOW_FILES:
        user_to_be_searched = None
        for user in lookup_table.users_data:
            if user.username == msg.message_content:
                user_to_be_searched = user
                break
        if user_to_be_searched is not None:
            return message(OK, user_to_be_searched.videos)
        else:
            return message(OK, [])
    elif msg.message_type == DOWNLOAD_REQUEST:
        # To be edited must send node ip
        username, filename = msg.message_content.split()
        list_ip_with_ports, file_size = get_download_ports_with_file_size(username, filename)
        return message(DOWNLOAD_REQUEST, [list_ip_with_ports, file_size])
    elif msg.message_type == UPLOAD_SUCCESS:
        for user in lookup_table.users_data:
            if user.username == msg.message_content[0]:
                user.videos.append(
                    video(f"{msg.message_content[0]}_{msg.message_content[1]}",
                          [get_node_by_ip_port(msg.message_content[2], msg.message_content[3])],
                          msg.message_content[4]))
                save_users_data()
                return message(OK, OK)
        print(lookup_table)


# master_tracker as server to get requests from users
def master_tracker_client():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://{MASTER_TRACKER_IP}:{MASTER_CLIENT_REP}")
    while True:
        msg = socket.recv_pyobj()
        reply = handle_message(msg)
        socket.send_pyobj(reply)


# master_tracker as subscriber.
def master_tracker_subscriber():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)

    socket.connect(f"tcp://{NODE_KEEPER_IP_1}:{NODE_KEEPER_MASTER_PUB_1}")
    socket.connect(f"tcp://{NODE_KEEPER_IP_2}:{NODE_KEEPER_MASTER_PUB_2}")
    socket.connect(f"tcp://{NODE_KEEPER_IP_3}:{NODE_KEEPER_MASTER_PUB_3}")
    socket.connect(f"tcp://{NODE_KEEPER_IP_4}:{NODE_KEEPER_MASTER_PUB_4}")
    socket.connect(f"tcp://{NODE_KEEPER_IP_5}:{NODE_KEEPER_MASTER_PUB_5}")

    filter_top = "10000"
    socket.setsockopt_string(zmq.SUBSCRIBE, filter_top)

    while True:
        msg = socket.recv_string()
        node_keeper_ip = msg.split()[1]
        node_keeper_port = msg.split()[2]
        for node_keeper in lookup_table.nodes_data:
            if node_keeper.nodeIP == node_keeper_ip and node_keeper_port in node_keeper.nodePorts:
                node_keeper.last_time = int(time())


# node_keeper sends success to update the lookup table.
def master_tracker_node_keeper():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://{MASTER_TRACKER_IP}:{MASTER_NODE_KEEPER_REP}")
    while True:
        try:
            msg = socket.recv_pyobj()
            reply = handle_message(msg)
            socket.send_pyobj(reply)
        except:
            while True:
                if not mutex.locked():
                    exit()


def save_users_data():
    with open("master_db.db", "wb") as file:
        pickle.dump(lookup_table.users_data, file)


def load_users_data():
    global lookup_table
    file = Path("master_db.db")
    if file.exists():
        with open("master_db.db", "rb") as f:
            lookup_table.users_data = pickle.load(f)


def main():
    load_users_data()
    print(lookup_table)
    Thread(target=update_alive).start()
    Thread(target=master_tracker_client).start()
    Thread(target=master_tracker_subscriber).start()
    Thread(target=master_tracker_node_keeper).start()


if __name__ == "__main__":
    main()
