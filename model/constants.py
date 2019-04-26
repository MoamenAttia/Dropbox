import socket

################# IP ###############################
MASTER_TRACKER_IP = socket.gethostbyname(socket.gethostname())

NODE_KEEPER_IP_1 = socket.gethostbyname(socket.gethostname())
NODE_KEEPER_IP_2 = socket.gethostbyname(socket.gethostname())
NODE_KEEPER_IP_3 = socket.gethostbyname(socket.gethostname())
NODE_KEEPER_IP_4 = socket.gethostbyname(socket.gethostname())
NODE_KEEPER_IP_5 = socket.gethostbyname(socket.gethostname())

################# MASTER PORTS #########################
MASTER_CLIENT_REP = "3000"  # to get clients' requests
MATER_NODE_KEEPER_SUB = "3002"  # to get alive
MASTER_NODE_KEEPER_REP = "3004"  # to get succes_message

################# NODE_KEEPER PORTS ####################
NODE_KEEPER_CLIENT_REP_1 = "2002"
NODE_KEEPER_MASTER_PUB_1 = "2004"
NODE_KEEPER_MASTER_REQ_1 = "2030"

NODE_KEEPER_CLIENT_REP_2 = "2006"
NODE_KEEPER_MASTER_PUB_2 = "2008"
NODE_KEEPER_MASTER_REQ_2 = "2032"

NODE_KEEPER_CLIENT_REP_3 = "2010"
NODE_KEEPER_MASTER_PUB_3 = "2012"
NODE_KEEPER_MASTER_REQ_3 = "2034"

NODE_KEEPER_CLIENT_REP_4 = "2014"
NODE_KEEPER_MASTER_PUB_4 = "2016"
NODE_KEEPER_MASTER_REQ_4 = "2036"

NODE_KEEPER_CLIENT_REP_5 = "2018"
NODE_KEEPER_MASTER_PUB_5 = "2020"
NODE_KEEPER_MASTER_REQ_5 = "2038"

################ CONSTANTS #############################
DOWNLOAD_REQUEST = "DOWNLOAD_REQUEST"
UPLOAD_REQUEST = "UPLOAD_REQUEST"

VIDEO = "VIDEO"
VIDEO_DONE = "VIDEO_DONE"  # send filename,username => to open a file in node.
VIDEO_NAME_REQUEST = "VIDEO_NAME_REQUEST"

ALIVE = "ALIVE"
UPLOAD_SUCCESS = "UPLOAD_SUCCESS"
UPLOAD_FAILED = "UPLOAD_FAILED"

PORT_RESERVATION_SUCCESS = "PORT_RESERVATION_SUCCESS"
PORT_RESERVATION_FAILED = "PORT_RESERVATION_FAILED"

OK = "OK"

SHOW_FILES = "SHOW_FILES"

DOWNLOAD_PROCESS = "DOWNLOAD_PROCESS"

CHUNK_SIZE = 1000000