import socket
import threading
import time
import sys


from load_balancer.server_info import ServerInfo


from load_balancer.strategies import (
    RoundRobinStrategy,
    LeastConnectionsStrategy,
    RandomStrategy,
    WeightedRoundRobinStrategy
)


from load_balancer.health_checker import HealthChecker
from load_balancer.metrics import Metrics


from monitoring.metrics_server import MetricsServer


class LoadBalancer:

    def __init__(self, host, port, strategy):

        self.host = host
        self.port = port
        self.strategy = strategy

        # Backend servers
        self.servers = []

        # Metrics
        self.metrics = Metrics()

        # Metrics API server
        self.metrics_server = MetricsServer(
            self.metrics,
            self.servers,
            host="127.0.0.1",
            port=9001
        )

        # Load balancer socket
        self.server_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.server_socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        self.server_socket.bind(
            (self.host, self.port)
        )

        self.server_socket.listen(20)

        self.running = True

        # Health checker
        self.health_checker = HealthChecker(
            self.servers,
            interval=5
        )

        # Terminal metrics thread
        self.stats_thread = threading.Thread(
            target=self.print_stats_periodically,
            daemon=True
        )

    # ==================================================
    # ADD SERVER
    # ==================================================

    def add_server(self, server):

        self.servers.append(server)

        print(
            f"[Load Balancer] Added Server "
            f"{server.server_id} "
            f"({server.host}:{server.port})"
        )

    # ==================================================
    # PERIODIC TERMINAL METRICS
    # ==================================================

    def print_stats_periodically(self):

        while self.running:

            time.sleep(10)

            self.metrics.print_stats()

    # ==================================================
    # START LOAD BALANCER
    # ==================================================

    def start(self):

        print(
            f"[Load Balancer] Strategy: "
            f"{self.strategy_name}"
        )

        print(
            f"[Load Balancer] Running on "
            f"{self.host}:{self.port}"
        )

        # ----------------------------------------------
        # Start health checker
        # ----------------------------------------------

        self.health_checker.start()

        # ----------------------------------------------
        # Start Metrics API
        # ----------------------------------------------

        metrics_thread = threading.Thread(
            target=self.metrics_server.start,
            daemon=True
        )

        metrics_thread.start()

        # ----------------------------------------------
        # Start terminal metrics
        # ----------------------------------------------

        self.stats_thread.start()

        # ----------------------------------------------
        # Accept clients
        # ----------------------------------------------

        while self.running:

            try:

                client_socket, client_address = (
                    self.server_socket.accept()
                )

                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(
                        client_socket,
                        client_address
                    )
                )

                client_thread.daemon = True
                client_thread.start()

            except OSError:

                if self.running:

                    print(
                        "[Load Balancer] Socket error"
                    )

                break

    # ==================================================
    # HANDLE CLIENT
    # ==================================================

    def handle_client(
        self,
        client_socket,
        client_address
    ):

        start_time = time.time()

        selected_server = None
        backend_socket = None

        try:

            # ------------------------------------------
            # Receive request
            # ------------------------------------------

            data = client_socket.recv(
                4096
            )

            if not data:

                client_socket.close()
                return

            request = data.decode()

            # ------------------------------------------
            # Select backend server
            # ------------------------------------------

            selected_server = (
                self.strategy.select_server(
                    self.servers
                )
            )

            # ------------------------------------------
            # No healthy server
            # ------------------------------------------

            if selected_server is None:

                print(
                    "[Load Balancer] "
                    "No healthy backend servers"
                )

                self.metrics.record_failure()

                client_socket.sendall(
                    b"No healthy backend servers available"
                )

                return

            # ------------------------------------------
            # Record request
            # ------------------------------------------

            self.metrics.record_request(
                selected_server.server_id
            )

            print(
                f"[Load Balancer] "
                f"{client_address} -> "
                f"Server {selected_server.server_id}"
            )

            # ------------------------------------------
            # Increment active connections
            # ------------------------------------------

            selected_server.increment_connections()

            try:

                # --------------------------------------
                # Connect to backend
                # --------------------------------------

                backend_socket = socket.socket(
                    socket.AF_INET,
                    socket.SOCK_STREAM
                )

                backend_socket.settimeout(10)

                backend_socket.connect(
                    (
                        selected_server.host,
                        selected_server.port
                    )
                )

                # --------------------------------------
                # Send request
                # --------------------------------------

                backend_socket.sendall(
                    request.encode()
                )

                # --------------------------------------
                # Receive response
                # --------------------------------------

                response = backend_socket.recv(
                    4096
                )

                if not response:

                    raise ConnectionError(
                        "Backend server returned "
                        "an empty response"
                    )

                # --------------------------------------
                # Send response to client
                # --------------------------------------

                client_socket.sendall(
                    response
                )

                # --------------------------------------
                # Calculate latency
                # --------------------------------------

                latency = (
                    time.time() - start_time
                ) * 1000

                # --------------------------------------
                # Record success
                # --------------------------------------

                self.metrics.record_success(
                    latency
                )

            except Exception as e:

                print(
                    f"[Load Balancer] "
                    f"Backend error on Server "
                    f"{selected_server.server_id}: "
                    f"{e}"
                )

                self.metrics.record_failure()

                # Mark server unhealthy
                selected_server.healthy = False

                try:

                    client_socket.sendall(
                        b"Backend server error"
                    )

                except Exception:
                    pass

            finally:

                # --------------------------------------
                # Decrement active connections
                # --------------------------------------

                selected_server.decrement_connections()

                if backend_socket is not None:

                    try:
                        backend_socket.close()

                    except Exception:
                        pass

        except Exception as e:

            print(
                f"[Load Balancer] "
                f"Client error: {e}"
            )

            self.metrics.record_failure()

            try:

                client_socket.sendall(
                    b"Load balancer error"
                )

            except Exception:
                pass

        finally:

            try:

                client_socket.close()

            except Exception:
                pass

    # ==================================================
    # STOP
    # ==================================================

    def stop(self):

        self.running = False

        # Stop health checker
        self.health_checker.stop()

        # Stop metrics API
        self.metrics_server.stop()

        # Close load balancer socket
        try:

            self.server_socket.close()

        except Exception:
            pass


# ======================================================
# STRATEGY CREATION
# ======================================================

def create_strategy(strategy_name):

    strategies = {

        "round_robin":
            RoundRobinStrategy(),

        "least_connections":
            LeastConnectionsStrategy(),

        "random":
            RandomStrategy(),

        "weighted":
            WeightedRoundRobinStrategy()
    }

    if strategy_name not in strategies:

        print(
            "\nInvalid strategy."
        )

        print(
            "\nAvailable strategies:"
        )

        print(
            "  round_robin"
        )

        print(
            "  least_connections"
        )

        print(
            "  random"
        )

        print(
            "  weighted"
        )

        sys.exit(1)

    return strategies[
        strategy_name
    ]


# ======================================================
# STRATEGY DISPLAY NAME
# ======================================================

def get_strategy_display_name(
    strategy_name
):

    names = {

        "round_robin":
            "ROUND ROBIN",

        "least_connections":
            "LEAST CONNECTIONS",

        "random":
            "RANDOM",

        "weighted":
            "WEIGHTED ROUND ROBIN"
    }

    return names[
        strategy_name
    ]


# ======================================================
# MAIN
# ======================================================

if __name__ == "__main__":

    # --------------------------------------------------
    # READ STRATEGY FROM COMMAND LINE
    # --------------------------------------------------

    if len(sys.argv) < 2:

        print(
            "\nUsage:"
        )

        print(
            "python -m load_balancer.load_balancer "
            "<strategy>"
        )

        print(
            "\nAvailable strategies:"
        )

        print(
            "  round_robin"
        )

        print(
            "  least_connections"
        )

        print(
            "  random"
        )

        print(
            "  weighted"
        )

        sys.exit(1)


    strategy_name = (
        sys.argv[1].lower()
    )


    # --------------------------------------------------
    # CREATE STRATEGY
    # --------------------------------------------------

    strategy = create_strategy(
        strategy_name
    )


    # --------------------------------------------------
    # CREATE LOAD BALANCER
    # --------------------------------------------------

    load_balancer = LoadBalancer(
        host="127.0.0.1",
        port=9000,
        strategy=strategy
    )


    # Store display name
    load_balancer.strategy_name = (
        get_strategy_display_name(
            strategy_name
        )
    )


    # --------------------------------------------------
    # SERVER 1
    # --------------------------------------------------

    server1 = ServerInfo(
        server_id=1,
        host="127.0.0.1",
        port=8001,
        weight=1
    )


    # --------------------------------------------------
    # SERVER 2
    # --------------------------------------------------

    server2 = ServerInfo(
        server_id=2,
        host="127.0.0.1",
        port=8002,
        weight=2
    )


    # --------------------------------------------------
    # SERVER 3
    # --------------------------------------------------

    server3 = ServerInfo(
        server_id=3,
        host="127.0.0.1",
        port=8003,
        weight=3
    )


    # --------------------------------------------------
    # ADD SERVERS
    # --------------------------------------------------

    load_balancer.add_server(
        server1
    )

    load_balancer.add_server(
        server2
    )

    load_balancer.add_server(
        server3
    )


    # --------------------------------------------------
    # START
    # --------------------------------------------------

    try:

        load_balancer.start()

    except KeyboardInterrupt:

        print(
            "\n[Load Balancer] "
            "Shutting down..."
        )

        load_balancer.stop()