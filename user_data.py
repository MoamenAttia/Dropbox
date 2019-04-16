from video import video
from node_data import node_data


class user_data(object):

    def __init__(self, username, userIP, userPorts):
        self.username = username
        self.userIP = userIP
        self.userPorts = userPorts
        self.videos = []

    def filterVideos(self, nodeIP):
        removed = []

        for video in self.videos:
            if video.nodeIP == nodeIP:
                removed.append(video)

        for video in removed:
            self.videos.remove(video)
        print("Videos Removed From user:", self.username)
