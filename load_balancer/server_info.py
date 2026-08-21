import threading


class ServerInfo:

    def __init__(self, server_id, host, port, weight=1):
        self.server_id = server_id
        self.host = host
        self.port = port
        self.weight = weight

        self.active_connections = 0
        self.healthy = True

        self.lock = threading.Lock()

    def increment_connections(self):
        with self.lock:
            self.active_connections += 1

    def decrement_connections(self):
        with self.lock:
            if self.active_connections > 0:
                self.active_connections -= 1

    def get_connections(self):
        with self.lock:
            return self.active_connections