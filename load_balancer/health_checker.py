import socket
import threading
import time


class HealthChecker:

    def __init__(self, servers, interval=5):

        self.servers = servers
        self.interval = interval
        self.running = True

    # ==================================================
    # CHECK ONE SERVER
    # ==================================================

    def check_server(self, server):

        sock = None

        try:

            sock = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            # Don't wait too long for a dead server
            sock.settimeout(2)

            # ------------------------------------------
            # CONNECT
            # ------------------------------------------

            sock.connect(
                (
                    server.host,
                    server.port
                )
            )

            # ------------------------------------------
            # SEND HEALTH CHECK
            # ------------------------------------------

            sock.sendall(
                b"HEALTH_CHECK"
            )

            # ------------------------------------------
            # WAIT FOR RESPONSE
            # ------------------------------------------

            response = sock.recv(1024)

            # Empty response means the server closed
            # the connection without responding.

            if not response:

                raise ConnectionError(
                    "Server returned empty response"
                )

            # ------------------------------------------
            # SERVER IS HEALTHY
            # ------------------------------------------

            if not server.healthy:

                print(
                    f"[Health Checker] "
                    f"Server {server.server_id} recovered"
                )

            server.healthy = True

        except (
            socket.timeout,
            ConnectionRefusedError,
            ConnectionResetError,
            ConnectionError,
            OSError
        ):

            # ------------------------------------------
            # SERVER IS DOWN
            # ------------------------------------------

            if server.healthy:

                print(
                    f"[Health Checker] "
                    f"Server {server.server_id} is DOWN"
                )

            server.healthy = False

        finally:

            if sock is not None:

                try:
                    sock.close()

                except Exception:
                    pass

    # ==================================================
    # HEALTH CHECK LOOP
    # ==================================================

    def run(self):

        print(
            "[Health Checker] Started"
        )

        while self.running:

            for server in self.servers:

                self.check_server(server)

            time.sleep(
                self.interval
            )

    # ==================================================
    # START
    # ==================================================

    def start(self):

        thread = threading.Thread(
            target=self.run,
            daemon=True
        )

        thread.start()

        return thread

    # ==================================================
    # STOP
    # ==================================================

    def stop(self):

        self.running = False

        print(
            "[Health Checker] Stopped"
        )