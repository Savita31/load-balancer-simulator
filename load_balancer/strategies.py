import random
import threading


class RoundRobinStrategy:

    def __init__(self):
        self.current_index = 0
        self.lock = threading.Lock()

    def select_server(self, servers):

        healthy_servers = [
            server
            for server in servers
            if server.healthy
        ]

        if not healthy_servers:
            return None

        with self.lock:

            server = healthy_servers[
                self.current_index
                % len(healthy_servers)
            ]

            self.current_index += 1

            return server


class LeastConnectionsStrategy:

    def select_server(self, servers):

        healthy_servers = [
            server
            for server in servers
            if server.healthy
        ]

        if not healthy_servers:
            return None

        return min(
            healthy_servers,
            key=lambda server: server.active_connections
        )


class RandomStrategy:

    def select_server(self, servers):

        healthy_servers = [
            server
            for server in servers
            if server.healthy
        ]

        if not healthy_servers:
            return None

        return random.choice(
            healthy_servers
        )


class WeightedRoundRobinStrategy:

    def __init__(self):

        self.current_index = 0
        self.lock = threading.Lock()

    def select_server(self, servers):

        healthy_servers = [
            server
            for server in servers
            if server.healthy
        ]

        if not healthy_servers:
            return None

        # Build the weighted server list.
        #
        # Example:
        # S1 weight=1
        # S2 weight=2
        # S3 weight=3
        #
        # becomes:
        #
        # [S1, S2, S2, S3, S3, S3]

        weighted_servers = []

        for server in healthy_servers:

            weight = max(
                1,
                int(server.weight)
            )

            weighted_servers.extend(
                [server] * weight
            )

        if not weighted_servers:
            return None

        with self.lock:

            server = weighted_servers[
                self.current_index
                % len(weighted_servers)
            ]

            self.current_index += 1

            return server