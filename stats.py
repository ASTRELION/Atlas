import time

class Stats:
    """Store runtime data for >botinfo"""
    def __init__(self):
        self.start_time = time.time()
        self.commands_processed = 0