import threading


class Metrics:

    def __init__(self):

        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0

        self.server_requests = {}

        self.total_latency = 0.0

        # Protect shared data because multiple
        # client threads update the metrics.
        self.lock = threading.Lock()

    # ==================================================
    # RECORD REQUEST
    # ==================================================

    def record_request(self, server_id):

        with self.lock:

            self.total_requests += 1

            if server_id not in self.server_requests:
                self.server_requests[server_id] = 0

            self.server_requests[server_id] += 1

    # ==================================================
    # RECORD SUCCESS
    # ==================================================

    def record_success(self, latency):

        with self.lock:

            self.successful_requests += 1

            self.total_latency += latency

    # ==================================================
    # RECORD FAILURE
    # ==================================================

    def record_failure(self):

        with self.lock:

            self.failed_requests += 1

    # ==================================================
    # GET AVERAGE LATENCY
    # ==================================================

    def get_average_latency(self):

        with self.lock:

            if self.successful_requests == 0:
                return 0.0

            return (
                self.total_latency
                / self.successful_requests
            )

    # ==================================================
    # RESET METRICS
    # ==================================================

    def reset(self):

        with self.lock:

            self.total_requests = 0

            self.successful_requests = 0

            self.failed_requests = 0

            self.server_requests.clear()

            self.total_latency = 0.0
    # ==================================================
    # PRINT STATISTICS
    # ==================================================

    def print_stats(self):

        # Take a snapshot of all values while holding
        # the lock.

        with self.lock:

            total_requests = self.total_requests

            successful_requests = (
                self.successful_requests
            )

            failed_requests = (
                self.failed_requests
            )

            total_latency = self.total_latency

            server_requests = (
                self.server_requests.copy()
            )

        # IMPORTANT:
        # Lock is released here.
        #
        # We calculate average latency outside the lock.
        # This prevents the deadlock we had before.

        if successful_requests == 0:

            average_latency = 0.0

        else:

            average_latency = (
                total_latency
                / successful_requests
            )

        # ==================================================
        # DISPLAY
        # ==================================================

        print()
        print("=" * 40)
        print("       LOAD BALANCER METRICS")
        print("=" * 40)

        print(
            f"Total Requests      : "
            f"{total_requests}"
        )

        print(
            f"Successful Requests : "
            f"{successful_requests}"
        )

        print(
            f"Failed Requests     : "
            f"{failed_requests}"
        )

        print(
            f"Average Latency     : "
            f"{average_latency:.2f} ms"
        )

        print()
        print("Requests per Server:")

        if server_requests:

            for server_id, count in sorted(
                server_requests.items()
            ):

                print(
                    f"  Server {server_id}: "
                    f"{count}"
                )

        else:

            print("  No requests yet.")

        print("=" * 40)