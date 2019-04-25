from message import message
from constants import *
from threading import Lock, Thread
from time import sleep, time
import zmq
from user_data import user_data
from video import *

from lookup import lookup

lookup_table = lookup()
mutex = Lock()


def is_alive(ip):
    for node_keeper in lookup_table.nodes_data:
        if node_keeper.nodeIP == ip:
            return node_keeper.alive
    return False


def get_download_ports_with_file_size(username, filename):
    mutex.acquire()
    video_name = f"{username}_{filename}"
    video_to_be_searched = None
    for user in lookup_table.users_data:
        if user.username == username:
            for vid in user.videos:
                if vid.filename == video_name:
                    video_to_be_searched = vid
                    break
            break
    for node_keeper_ip in video_to_be_searched.node_ips:
        if is_alive(node_keeper_ip):
            if node_keeper_ip == NODE_KEEPER_IP_1:
                mutex.release()
                return [NODE_KEEPER_IP_1, NODE_KEEPER_CLIENT_REP_1, video_to_be_searched.file_size]
            elif node_keeper_ip == NODE_KEEPER_IP_2:
                mutex.release()
                return [NODE_KEEPER_IP_2, NODE_KEEPER_CLIENT_REP_2, video_to_be_searched.file_size]
            elif node_keeper_ip == NODE_KEEPER_IP_3:
                mutex.release()
                return [NODE_KEEPER_IP_3, NODE_KEEPER_CLIENT_REP_3, video_to_be_searched.file_size]
            elif node_keeper_ip == NODE_KEEPER_IP_4:
                mutex.release()
                return [NODE_KEEPER_IP_4, NODE_KEEPER_CLIENT_REP_4, video_to_be_searched.file_size]
            elif node_keeper_ip == NODE_KEEPER_IP_5:
                mutex.release()
                return [NODE_KEEPER_IP_5, NODE_KEEPER_CLIENT_REP_5, video_to_be_searched.file_size]

    mutex.release()
    return [None, None]


def get_free_port():
    mutex.acquire()
    for node_keeper in lookup_table.nodes_data:
        if node_keeper.alive:
            if node_keeper.nodeIP == NODE_KEEPER_IP_1:
                mutex.release()
                return [NODE_KEEPER_IP_1, NODE_KEEPER_CLIENT_REP_1]
            elif node_keeper.nodeIP == NODE_KEEPER_IP_2:
                mutex.release()
                return [NODE_KEEPER_IP_2, NODE_KEEPER_CLIENT_REP_2]
            elif node_keeper.nodeIP == NODE_KEEPER_IP_3:
                mutex.release()
                return [NODE_KEEPER_IP_3, NODE_KEEPER_CLIENT_REP_3]
            elif node_keeper.nodeIP == NODE_KEEPER_IP_4:
                mutex.release()
                return [NODE_KEEPER_IP_4, NODE_KEEPER_CLIENT_REP_4]
            elif node_keeper.nodeIP == NODE_KEEPER_IP_5:
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


# master_tracker as server to get requests from users
def master_tracker_client():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://{MASTER_TRACKER_IP}:{MASTER_CLIENT_REP}")
    while True:
        msg = socket.recv_pyobj()
        print(msg.message_type)
        if msg.message_type == UPLOAD_REQUEST:
            # Add User anyway
            flag = False
            for user in lookup_table.users_data:
                if user.username == msg.message_content:
                    flag = True
                    break
            if not flag:
                lookup_table.users_data.append(user_data(msg.message_content))
            # To be edited must send node ip
            [node_keeper_ip, node_keeper_port] = get_free_port()
            msg = message(UPLOAD_REQUEST, [node_keeper_ip, node_keeper_port])
            socket.send_pyobj(msg)
            print(f"ip:{node_keeper_ip}, port:{node_keeper_port} SENT")
        elif msg.message_type == SHOW_FILES:
            user_to_be_searched = None
            for user in lookup_table.users_data:
                if user.username == msg.message_content:
                    user_to_be_searched = user
                    break
            if user_to_be_searched is not None:
                msg = message(OK, user_to_be_searched.videos)
                socket.send_pyobj(msg)
            else:
                msg = message(OK, [])
                socket.send_pyobj(msg)
        elif msg.message_type == DOWNLOAD_REQUEST:
            # To be edited must send node ip
            username, filename = msg.message_content.split()
            node_keeper_ip, node_keeper_port, file_size = get_download_ports_with_file_size(username, filename)
            msg = message(DOWNLOAD_REQUEST, [node_keeper_ip, node_keeper_port, file_size])
            socket.send_pyobj(msg)
            print(f"ip:{node_keeper_ip}, port:{node_keeper_port} SENT, file_size: {file_size}")


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


def handle_message(msg):
    if msg.message_type == UPLOAD_SUCCESS:
        for user in lookup_table.users_data:
            if user.username == msg.message_content[0]:
                user.videos.append(
                    video(f"{msg.message_content[0]}_{msg.message_content[1]}", [msg.message_content[2]],
                          msg.message_content[3]))
                break
        print(lookup_table)


# node_keeper sends success to update the lookup table.
def master_tracker_node_keeper():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://{MASTER_TRACKER_IP}:{MASTER_NODE_KEEPER_REP}")
    while True:
        msg = socket.recv_pyobj()
        handle_message(msg)
        print("Sending OK")
        socket.send_pyobj(message(OK, OK))


def main():
    Thread(target=update_alive).start()
    Thread(target=master_tracker_client).start()
    Thread(target=master_tracker_subscriber).start()
    Thread(target=master_tracker_node_keeper).start()


if __name__ == "__main__":
    main()
