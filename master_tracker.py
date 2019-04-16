from lookup import lookup


class master_tracker(object):
    def __init__(self):
        self.lookup = lookup()

    def update(self):
        self.lookup.filter()
