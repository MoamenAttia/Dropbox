class message(object):
    def __init__(self, message_type, message_content, message_from_ip, message_from_port):
        self.message_type = message_type
        self.message_content = message_content
        self.message_from_ip = message_from_ip
        self.message_from_port = message_from_port
