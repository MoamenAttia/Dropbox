class video(object):
    def __init__(self, filename, node_ips):
        self.filename = filename
        self.node_ips = node_ips

    def printVideo(self):
        print(f"video filename:{self.filename} video IPs:{self.node_ips}")