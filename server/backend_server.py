import socket
import threading
import sys
import time


class BackendServer:

    def __init__(self, server_id, host, port, processing_time=2):

        self.server_id = server_id
        self.host = host
        self.port = port
        self.processing_time = processing_time

        self.server_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        # Allow the server to reuse the port after restarting
        self.server_socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        self.server_socket.bind(
            (self.host, self.port)
        )

        self.server_socket.listen(10)

        self.running = True

    def start(self):

        print(
            f"[Server {self.server_id}] "
            f"Running on {self.host}:{self.port}"
        )

        while self.running:

            try:
                client_socket, client_address = (
                    self.server_socket.accept()
                )

                # Handle each connection in its own thread
                thread = threading.Thread(
                    target=self.handle_request,
                    args=(client_socket, client_address)
                )

                thread.daemon = True
                thread.start()

            except OSError:

                if self.running:
                    print(
                        f"[Server {self.server_id}] "
                        f"Socket error"
                    )

                break

    def handle_request(
        self,
        client_socket,
        client_address
    ):

        try:

            data = client_socket.recv(4096)

            if not data:
                client_socket.close()
                return

            request = data.decode().strip()

            # ---------------------------------------
            # HEALTH CHECK
            # ---------------------------------------

            if request == "HEALTH_CHECK":

                client_socket.sendall(
                    b"HEALTHY"
                )

                client_socket.close()

                return

            # ---------------------------------------
            # NORMAL CLIENT REQUEST
            # ---------------------------------------

            print(
                f"[Server {self.server_id}] "
                f"Received: {request}"
            )

            # Simulate server processing time
            time.sleep(
                self.processing_time
            )

            response = (
                f"Response from Server "
                f"{self.server_id}"
            )

            client_socket.sendall(
                response.encode()
            )

        except Exception as e:

            print(
                f"[Server {self.server_id}] "
                f"Error: {e}"
            )

            try:
                client_socket.sendall(
                    b"Backend server error"
                )

            except Exception:
                pass

        finally:

            client_socket.close()

    def stop(self):

        self.running = False

        try:
            self.server_socket.close()
        except Exception:
            pass


if __name__ == "__main__":

    if len(sys.argv) < 4:

        print(
            "Usage: "
            "python backend_server.py "
            "<server_id> <port> <processing_time>"
        )

        sys.exit(1)

    server_id = int(sys.argv[1])

    port = int(sys.argv[2])

    processing_time = float(
        sys.argv[3]
    )

    server = BackendServer(
        server_id=server_id,
        host="127.0.0.1",
        port=port,
        processing_time=processing_time
    )

    try:

        server.start()

    except KeyboardInterrupt:

        print(
            f"\n[Server {server.server_id}] "
            f"Shutting down..."
        )

        server.stop()