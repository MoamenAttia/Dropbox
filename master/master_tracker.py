from libraries import *

lookup_table = lookup()
mutex = Lock()


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
    list_ip_with_ports = []
    for node_keeper in video_to_be_searched.nodes:
        if is_alive(node_keeper.node.nodeIP, node_keeper.node.nodePorts[0]):
            if does_node_have_ip_have_port(node_keeper.node, NODE_KEEPER_IP_1, NODE_KEEPER_CLIENT_REP_1):
                list_ip_with_ports.append((NODE_KEEPER_IP_1, NODE_KEEPER_CLIENT_REP_1))
            elif does_node_have_ip_have_port(node_keeper.node, NODE_KEEPER_IP_2, NODE_KEEPER_CLIENT_REP_2):
                list_ip_with_ports.append((NODE_KEEPER_IP_2, NODE_KEEPER_CLIENT_REP_2))
            elif does_node_have_ip_have_port(node_keeper.node, NODE_KEEPER_IP_3, NODE_KEEPER_CLIENT_REP_3):
                list_ip_with_ports.append((NODE_KEEPER_IP_3, NODE_KEEPER_CLIENT_REP_3))
            elif does_node_have_ip_have_port(node_keeper.node, NODE_KEEPER_IP_4, NODE_KEEPER_CLIENT_REP_4):
                list_ip_with_ports.append((NODE_KEEPER_IP_4, NODE_KEEPER_CLIENT_REP_4))
            elif does_node_have_ip_have_port(node_keeper.node, NODE_KEEPER_IP_5, NODE_KEEPER_CLIENT_REP_5):
                list_ip_with_ports.append((NODE_KEEPER_IP_5, NODE_KEEPER_CLIENT_REP_5))
    return list_ip_with_ports, video_to_be_searched.file_size


def get_free_port():
    shuffle(lookup_table.nodes_data)
    for node_keeper in lookup_table.nodes_data:
        if node_keeper.alive:
            if does_node_have_ip_have_port(node_keeper, NODE_KEEPER_IP_1, NODE_KEEPER_CLIENT_REP_1):
                return [NODE_KEEPER_IP_1, NODE_KEEPER_CLIENT_REP_1]
            elif does_node_have_ip_have_port(node_keeper, NODE_KEEPER_IP_2, NODE_KEEPER_CLIENT_REP_2):
                return [NODE_KEEPER_IP_2, NODE_KEEPER_CLIENT_REP_2]
            elif does_node_have_ip_have_port(node_keeper, NODE_KEEPER_IP_3, NODE_KEEPER_CLIENT_REP_3):
                return [NODE_KEEPER_IP_3, NODE_KEEPER_CLIENT_REP_3]
            elif does_node_have_ip_have_port(node_keeper, NODE_KEEPER_IP_4, NODE_KEEPER_CLIENT_REP_4):
                return [NODE_KEEPER_IP_4, NODE_KEEPER_CLIENT_REP_4]
            elif does_node_have_ip_have_port(node_keeper, NODE_KEEPER_IP_5, NODE_KEEPER_CLIENT_REP_5):
                return [NODE_KEEPER_IP_5, NODE_KEEPER_CLIENT_REP_5]
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
                    print(nodes)

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
        mutex.acquire()
        for node_keeper in lookup_table.nodes_data:
            if node_keeper.nodeIP == node_keeper_ip and node_keeper_port in node_keeper.nodePorts:
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
    pass
    # with open("master_db.db", "wb") as file:
    #     pickle.dump(lookup_table.users_data, file)


def load_users_data():
    global lookup_table
    file = Path("master_db.db")
    if file.exists():
        with open("master_db.db", "rb") as f:
            lookup_table.users_data = pickle.load(f)


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
                        nodes.append(temp_node.node)
                    for temp_node in nodes:
                        if temp_node.alive:
                            node_to_send = temp_node
                        nodes_to_be_appended.append(rep_node_data(temp_node, False, int(time())))
                    for node in lookup_table.nodes_data:
                        if max_nodes >= 3:
                            break
                        if node.alive and node not in nodes:
                            if does_node_have_ip_have_port(node, NODE_KEEPER_IP_1, NODE_KEEPER_CLIENT_REP_1):
                                nodes_to_be_appended.append(rep_node_data(node, True, int(time())))
                                max_nodes += 1
                                ip_ports.append([node.nodeIP, NODE_KEEPER_CLIENT_REP_1])
                            elif does_node_have_ip_have_port(node, NODE_KEEPER_IP_2, NODE_KEEPER_CLIENT_REP_2):
                                nodes_to_be_appended.append(rep_node_data(node, True, int(time())))
                                max_nodes += 1
                                ip_ports.append([node.nodeIP, NODE_KEEPER_CLIENT_REP_2])
                            elif does_node_have_ip_have_port(node, NODE_KEEPER_IP_3, NODE_KEEPER_CLIENT_REP_3):
                                nodes_to_be_appended.append(rep_node_data(node, True, int(time())))
                                max_nodes += 1
                                ip_ports.append([node.nodeIP, NODE_KEEPER_CLIENT_REP_3])
                            elif does_node_have_ip_have_port(node, NODE_KEEPER_IP_4, NODE_KEEPER_CLIENT_REP_4):
                                nodes_to_be_appended.append(rep_node_data(node, True, int(time())))
                                max_nodes += 1
                                ip_ports.append([node.nodeIP, NODE_KEEPER_CLIENT_REP_4])
                            elif does_node_have_ip_have_port(node, NODE_KEEPER_IP_5, NODE_KEEPER_CLIENT_REP_5):
                                nodes_to_be_appended.append(rep_node_data(node, True, int(time())))
                                max_nodes += 1
                                ip_ports.append([node.nodeIP, NODE_KEEPER_CLIENT_REP_5])

                    if len(ip_ports) > 0:
                        context = zmq.Context()
                        socket = context.socket(zmq.REQ)
                        node = node_to_send
                        node.printInfo()
                        if does_node_have_ip_have_port(node, NODE_KEEPER_IP_1, NODE_KEEPER_CLIENT_REP_1):
                            socket.connect(f"tcp://{node.nodeIP}:{NODE_KEEPER_CLIENT_REP_1}")
                        elif does_node_have_ip_have_port(node, NODE_KEEPER_IP_2, NODE_KEEPER_CLIENT_REP_2):
                            socket.connect(f"tcp://{node.nodeIP}:{NODE_KEEPER_CLIENT_REP_2}")
                        elif does_node_have_ip_have_port(node, NODE_KEEPER_IP_3, NODE_KEEPER_CLIENT_REP_3):
                            socket.connect(f"tcp://{node.nodeIP}:{NODE_KEEPER_CLIENT_REP_3}")
                        elif does_node_have_ip_have_port(node, NODE_KEEPER_IP_4, NODE_KEEPER_CLIENT_REP_4):
                            socket.connect(f"tcp://{node.nodeIP}:{NODE_KEEPER_CLIENT_REP_4}")
                        elif does_node_have_ip_have_port(node, NODE_KEEPER_IP_5, NODE_KEEPER_CLIENT_REP_5):
                            socket.connect(f"tcp://{node.nodeIP}:{NODE_KEEPER_CLIENT_REP_5}")

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


def main():
    load_users_data()
    Thread(target=update_alive).start()
    Thread(target=master_tracker_client).start()
    Thread(target=master_tracker_subscriber).start()
    Thread(target=master_tracker_node_keeper).start()
    Thread(target=check_replication).start()
    Thread(target=delete_false_records).start()


if __name__ == "__main__":
    main()
