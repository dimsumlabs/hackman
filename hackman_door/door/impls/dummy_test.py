class Door:

    def __init__(self):
        self.opened = None

    def open(self, open_time=None):
        self.opened = True

    def close(self):
        self.opened = False
