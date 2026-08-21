import socket
import concurrent.futures
import time


HOST = "127.0.0.1"
PORT = 9000

TOTAL_REQUESTS = 20


def send_request(request_id):

    start_time = time.time()

    try:

        client_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        client_socket.settimeout(15)

        client_socket.connect(
            (HOST, PORT)
        )

        message = f"Request {request_id}"

        client_socket.sendall(
            message.encode()
        )

        response = client_socket.recv(4096)

        latency = (
            time.time() - start_time
        ) * 1000

        client_socket.close()

        return {
            "success": True,
            "latency": latency,
            "response": response.decode()
        }

    except Exception as e:

        return {
            "success": False,
            "latency": 0,
            "response": str(e)
        }


def run_test():

    print("=" * 50)
    print("       LOAD BALANCER STRATEGY TEST")
    print("=" * 50)

    print(
        f"Sending {TOTAL_REQUESTS} requests..."
    )

    start_time = time.time()

    results = []

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=TOTAL_REQUESTS
    ) as executor:

        futures = [
            executor.submit(
                send_request,
                i
            )
            for i in range(1, TOTAL_REQUESTS + 1)
        ]

        for future in concurrent.futures.as_completed(
            futures
        ):

            results.append(
                future.result()
            )

    total_time = (
        time.time() - start_time
    ) * 1000

    successful = [
        result
        for result in results
        if result["success"]
    ]

    failed = [
        result
        for result in results
        if not result["success"]
    ]

    # ------------------------------------------
    # LATENCY
    # ------------------------------------------

    if successful:

        latencies = [
            result["latency"]
            for result in successful
        ]

        average_latency = (
            sum(latencies)
            / len(latencies)
        )

        min_latency = min(latencies)
        max_latency = max(latencies)

    else:

        average_latency = 0
        min_latency = 0
        max_latency = 0

    # ------------------------------------------
    # SERVER DISTRIBUTION
    # ------------------------------------------

    server_counts = {}

    for result in successful:

        response = result["response"]

        if "Server 1" in response:
            server_counts["Server 1"] = (
                server_counts.get("Server 1", 0) + 1
            )

        elif "Server 2" in response:
            server_counts["Server 2"] = (
                server_counts.get("Server 2", 0) + 1
            )

        elif "Server 3" in response:
            server_counts["Server 3"] = (
                server_counts.get("Server 3", 0) + 1
            )

    # ------------------------------------------
    # RESULTS
    # ------------------------------------------

    print()
    print("=" * 50)
    print("RESULTS")
    print("=" * 50)

    print(
        f"Total requests : {TOTAL_REQUESTS}"
    )

    print(
        f"Successful     : {len(successful)}"
    )

    print(
        f"Failed         : {len(failed)}"
    )

    print(
        f"Average latency: "
        f"{average_latency:.2f} ms"
    )

    print(
        f"Minimum latency: "
        f"{min_latency:.2f} ms"
    )

    print(
        f"Maximum latency: "
        f"{max_latency:.2f} ms"
    )

    print(
        f"Total test time: "
        f"{total_time:.2f} ms"
    )

    print()
    print("Server distribution:")

    for server in [
        "Server 1",
        "Server 2",
        "Server 3"
    ]:

        count = server_counts.get(
            server,
            0
        )

        print(
            f"  {server}: {count}"
        )

    print("=" * 50)


if __name__ == "__main__":

    run_test()