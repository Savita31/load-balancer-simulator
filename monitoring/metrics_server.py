import json
import socket
import threading


class MetricsServer:

    def __init__(
        self,
        metrics,
        servers,
        host="127.0.0.1",
        port=9001
    ):

        self.metrics = metrics
        self.servers = servers

        self.host = host
        self.port = port

        self.running = True

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

        self.server_socket.listen(10)

    # ==================================================
    # START METRICS SERVER
    # ==================================================

    def start(self):

        print(
            f"[Metrics API] Running on "
            f"{self.host}:{self.port}"
        )

        while self.running:

            try:

                client_socket, client_address = (
                    self.server_socket.accept()
                )

                thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket,)
                )

                thread.daemon = True
                thread.start()

            except OSError:

                if self.running:

                    print(
                        "[Metrics API] Socket error"
                    )

                break

    # ==================================================
    # HANDLE HTTP REQUEST
    # ==================================================

    def handle_client(self, client_socket):

        try:

            request = client_socket.recv(
                4096
            ).decode()

            # ==========================================
            # GET /reset
            # ==========================================

            if request.startswith(
                "GET /reset"
            ):

                self.metrics.reset()

                body = json.dumps(
                    {
                        "status": "success",
                        "message": "Metrics reset"
                    },
                    indent=4
                )

                body_bytes = body.encode(
                    "utf-8"
                )

                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: application/json\r\n"
                    "Access-Control-Allow-Origin: *\r\n"
                    f"Content-Length: {len(body_bytes)}\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                ).encode("utf-8") + body_bytes

                client_socket.sendall(
                    response
                )

                return

            # ==========================================
            # GET /metrics
            # ==========================================

            elif request.startswith(
                "GET /metrics"
            ):

                response_data = (
                    self.get_metrics()
                )

                body = json.dumps(
                    response_data,
                    indent=4
                )

                body_bytes = body.encode(
                    "utf-8"
                )

                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: application/json\r\n"
                    "Access-Control-Allow-Origin: *\r\n"
                    f"Content-Length: {len(body_bytes)}\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                ).encode("utf-8") + body_bytes

            # ==========================================
            # GET /
            # ==========================================

            elif request.startswith(
                "GET / "
            ):

                body = json.dumps(
                    {
                        "service":
                            "Load Balancer Metrics API",

                        "status":
                            "running",

                        "endpoint":
                            "/metrics",

                        "reset_endpoint":
                            "/reset"
                    },
                    indent=4
                )

                body_bytes = body.encode(
                    "utf-8"
                )

                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: application/json\r\n"
                    "Access-Control-Allow-Origin: *\r\n"
                    f"Content-Length: {len(body_bytes)}\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                ).encode("utf-8") + body_bytes

            # ==========================================
            # NOT FOUND
            # ==========================================

            else:

                body = json.dumps(
                    {
                        "error":
                            "Not Found",

                        "message":
                            "Use GET /metrics or GET /reset"
                    },
                    indent=4
                )

                body_bytes = body.encode(
                    "utf-8"
                )

                response = (
                    "HTTP/1.1 404 Not Found\r\n"
                    "Content-Type: application/json\r\n"
                    "Access-Control-Allow-Origin: *\r\n"
                    f"Content-Length: {len(body_bytes)}\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                ).encode("utf-8") + body_bytes

            client_socket.sendall(
                response
            )

        except Exception as e:

            print(
                f"[Metrics API] "
                f"Request error: {e}"
            )

        finally:

            try:

                client_socket.close()

            except Exception:

                pass

    # ==================================================
    # GET METRICS
    # ==================================================

    def get_metrics(self):

        # ------------------------------------------
        # TAKE THREAD-SAFE METRICS SNAPSHOT
        # ------------------------------------------

        with self.metrics.lock:

            total_requests = (
                self.metrics.total_requests
            )

            successful_requests = (
                self.metrics.successful_requests
            )

            failed_requests = (
                self.metrics.failed_requests
            )

            total_latency = (
                self.metrics.total_latency
            )

            server_requests = (
                self.metrics.server_requests.copy()
            )

        # ------------------------------------------
        # CALCULATE AVERAGE LATENCY
        # ------------------------------------------

        if successful_requests > 0:

            average_latency = (
                total_latency
                / successful_requests
            )

        else:

            average_latency = 0.0

        # ------------------------------------------
        # SERVER HEALTH INFORMATION
        # ------------------------------------------

        servers = {}

        for server in self.servers:

            servers[
                str(server.server_id)
            ] = {

                "healthy":
                    server.healthy,

                "active_connections":
                    server.active_connections,

                "requests":
                    server_requests.get(
                        server.server_id,
                        0
                    )
            }

        # ------------------------------------------
        # RETURN METRICS
        # ------------------------------------------

        return {

            "total_requests":
                total_requests,

            "successful_requests":
                successful_requests,

            "failed_requests":
                failed_requests,

            "average_latency_ms":
                round(
                    average_latency,
                    2
                ),

            "servers":
                servers
        }

    # ==================================================
    # STOP
    # ==================================================

    def stop(self):

        self.running = False

        try:

            self.server_socket.close()

        except Exception:

            pass