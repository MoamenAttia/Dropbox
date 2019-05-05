from libraries import *

lookup_table = lookup()
mutex = Lock()

sub_context = zmq.Context()
sub_socket = sub_context.socket(zmq.SUB)


def does_node_have_ip_have_port(node, node_ip, node_port):
    if node is None:
        return False
    if node.nodeIP == node_ip and node_port in node.nodePorts:
        return True
    return False


def get_node_by_ip_port(node_ip, node_port):
    for node_keeper in lookup_table.nodes_data:
        if node_keeper.nodeIP == node_ip and node_port in node_keeper.nodePorts:
            return node_keeper
    return None


def is_alive(ip, port):
    for node_keeper in lookup_table.nodes_data:
        if node_keeper.nodeIP == ip and port in node_keeper.nodePorts:
            return node_keeper.alive
    return False


def get_video_by_user_file(username, filename):
    for user in lookup_table.users_data:
        if user.username == username:
            for vid in user.videos:
                if vid.filename == filename:
                    return vid
    return None


def get_download_ports_with_file_size(username, filename):
    video_to_be_searched = get_video_by_user_file(username, filename)
    if video_to_be_searched is None:
        return None, None
    list_ip_with_ports = []
    for node_keeper in video_to_be_searched.nodes:
        if is_alive(node_keeper.node.nodeIP, node_keeper.node.nodePorts[0]) and not node_keeper.pending:
            list_ip_with_ports.append((node_keeper.node.nodeIP, node_keeper.node.nodePorts[0]))
            list_ip_with_ports.append((node_keeper.node.nodeIP, node_keeper.node.nodePorts[1]))
            list_ip_with_ports.append((node_keeper.node.nodeIP, node_keeper.node.nodePorts[2]))
    return list_ip_with_ports, video_to_be_searched.file_size


def get_free_port():
    shuffle(lookup_table.nodes_data)
    for node_keeper in lookup_table.nodes_data:
        if node_keeper.alive:
            shuffled_ports = [node_keeper.nodePorts[7], node_keeper.nodePorts[8], node_keeper.nodePorts[9]]
            return [node_keeper.nodeIP, shuffled_ports[0]]
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
        sleep(1)


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
                vid = get_video_by_user_file(msg.message_content[0], msg.message_content[1])
                if vid is None:
                    nodes = list()
                    nodes.append(
                        rep_node_data(get_node_by_ip_port(msg.message_content[2], msg.message_content[3]), False, 0))
                    user.videos.append(
                        video(f"{msg.message_content[1]}",
                              nodes,
                              msg.message_content[4]))
                else:
                    for node in vid.nodes:
                        if does_node_have_ip_have_port(node.node, msg.message_content[2], msg.message_content[3]):
                            node.pending = False
                save_users_data()
                return message(OK, OK)
    elif msg.message_type == NEW_NODE:
        node_ip = msg.message_content[0]
        node_ports = msg.message_content[1]
        print(f"{NEW_NODE} REQUEST ip: {node_ip} ports: {node_ports}")
        if get_node_by_ip_port(node_ip, node_ports[0]) is None:
            lookup_table.nodes_data.append(node_data(node_ip, node_ports))
            sub_socket.connect(f"tcp://{node_ip}:{node_ports[6]}")
            print(f"{NEW_NODE} Added to Lookup table")
            save_users_data()
        return message(OK, OK)


# master_tracker as server to get requests from users
def master_tracker_client():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{MASTER_CLIENT_REP}")
    while True:
        msg = socket.recv_pyobj()
        mutex.acquire()
        reply = handle_message(msg)
        mutex.release()
        socket.send_pyobj(reply)


# master_tracker as subscriber.
def master_tracker_subscriber():
    filter_top = "10000"
    sub_socket.setsockopt_string(zmq.SUBSCRIBE, filter_top)
    while True:
        msg = sub_socket.recv_string()
        node_keeper_ip = msg.split()[1]
        node_keeper_port = msg.split()[2]
        mutex.acquire()
        for node_keeper in lookup_table.nodes_data:
            if does_node_have_ip_have_port(node_keeper, node_keeper_ip, node_keeper_port):
                node_keeper.last_time = int(time())
        mutex.release()


# node_keeper sends success to update the lookup table.
def master_tracker_node_keeper():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{MASTER_NODE_KEEPER_REP}")
    while True:
        msg = socket.recv_pyobj()
        mutex.acquire()
        reply = handle_message(msg)
        mutex.release()
        socket.send_pyobj(reply)


def save_users_data():
    with open("master_db.db", "wb") as file:
        pickle.dump(lookup_table, file)


def load_users_data():
    global lookup_table
    file = Path("master_db.db")
    if file.exists():
        with open("master_db.db", "rb") as f:
            lookup_table = pickle.load(f)
            for node in lookup_table.nodes_data:
                sub_socket.connect(f"tcp://{node.nodeIP}:{node.nodePorts[6]}")
    else:
        lookup_table = lookup()
    print(lookup_table)


def check_replication():
    while True:
        mutex.acquire()
        for user in lookup_table.users_data:
            for vid in user.videos:
                ip_ports = []
                nodes_to_be_appended = []
                cnt = 0
                vid.nodes = list(vid.nodes)

                for item in vid.nodes:
                    if item.node.alive:
                        cnt += 1

                if cnt < 3 and cnt != 0:
                    node_to_send = None
                    max_nodes = cnt
                    nodes = []
                    for temp_node in vid.nodes:
                        if temp_node.node.alive and not temp_node.pending:
                            node_to_send = temp_node.node
                        nodes.append(temp_node.node)
                        nodes_to_be_appended.append(temp_node)

                    for node in lookup_table.nodes_data:
                        if max_nodes >= 3:
                            break
                        if node.alive and node not in nodes:
                            nodes_to_be_appended.append(rep_node_data(node, True, int(time())))
                            max_nodes += 1
                            replication_ports = [node.nodePorts[3], node.nodePorts[4], node.nodePorts[5]]
                            shuffle(replication_ports)
                            ip_ports.append([node.nodeIP, replication_ports[0]])

                    if len(ip_ports) > 0:
                        context = zmq.Context()
                        socket = context.socket(zmq.REQ)
                        node = node_to_send
                        node.printInfo()
                        replication_ports = [node.nodePorts[3], node.nodePorts[4], node.nodePorts[5]]
                        shuffle(replication_ports)
                        socket.connect(f"tcp://{node.nodeIP}:{replication_ports[0]}")
                        vid.nodes = nodes_to_be_appended
                        save_users_data()
                        msg = message(REPLICATION_REQUEST, [ip_ports, user.username, vid.filename])
                        print(f"message content : {msg.message_content}")
                        socket.send_pyobj(msg)
                        response = socket.recv_pyobj()
                        print(f"message content : response from replication {response.message_type}")

        mutex.release()
        sleep(2)


def delete_false_records():
    while True:
        mutex.acquire()
        for user in lookup_table.users_data:
            for vid in user.videos:
                vid.nodes = [i for i in vid.nodes if (not i.pending) or (i.pending and int(time()) - i.fromTime <= 60)]
        mutex.release()
        sleep(10)


def welcome():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{MASTER_WELCOME_PORT}")
    while True:
        msg = socket.recv_pyobj()
        reply = handle_message(msg)
        socket.send_pyobj(reply)


def main():
    load_users_data()
    Thread(target=welcome).start()
    Thread(target=update_alive).start()
    Thread(target=master_tracker_client).start()
    Thread(target=master_tracker_subscriber).start()
    Thread(target=master_tracker_node_keeper).start()
    Thread(target=check_replication).start()
    Thread(target=delete_false_records).start()


if __name__ == "__main__":
    main()
