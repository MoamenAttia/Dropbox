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
        mutex.acquire()
        for node_keeper in lookup_table.nodes_data:
            if int(time()) - node_keeper.last_time <= 2:
                node_keeper.alive = True
                node_keeper.last_time = int(time())
            else:
                node_keeper.alive = False
        mutex.release()
        sleep(1)


# master_tracker as server to get requests from users.s
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


# master_tracker as subscriber.
def master_tracker_subscriber():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://{NODE_KEEPER_IP_1}:{NODE_KEEPER_MASTER_PUB_1}")
    print(f"{NODE_KEEPER_IP_1} ,{NODE_KEEPER_MASTER_PUB_1}")
    filter_top = "10000"
    socket.setsockopt_string(zmq.SUBSCRIBE, filter_top)

    while True:
        node_keeper_ip = socket.recv_string().split()[1]
        for node_keeper in lookup_table.nodes_data:
            if node_keeper.nodeIP == node_keeper_ip:
                node_keeper.last_time = int(time())


def handle_message(msg):
    if msg.message_type == UPLOAD_SUCCESS:
        for user in lookup_table.users_data:
            if user.username == msg.message_content[0]:
                user.videos.append(
                    video(f"{msg.message_content[0]}_{msg.message_content[1]}", [msg.message_content[2]]))
                break
        lookup_table.printInfo()


# node_keeper sends success to update the lookup table.
def master_tracker_node_keeper():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://{MASTER_TRACKER_IP}:{MASTER_NODE_KEEPER_REP}")
    while True:
        msg = socket.recv_pyobj()
        handle_message(msg)
        socket.send_pyobj(message(OK, OK))


def main():
    Thread(target=update_alive).start()
    Thread(target=master_tracker_client).start()
    Thread(target=master_tracker_subscriber).start()
    Thread(target=master_tracker_node_keeper).start()


if __name__ == "__main__":
    main()
