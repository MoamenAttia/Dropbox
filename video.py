class video(object):
    def __init__(self, filename, node_ips, file_size):
        self.filename = filename
        self.node_ips = node_ips
        self.file_size = file_size

    def printVideo(self):
        print(f"video filename:{self.filename} video IPs:{self.node_ips}")
