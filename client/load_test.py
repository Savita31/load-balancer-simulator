import socket
import threading
import time
import sys


HOST = "127.0.0.1"
PORT = 9000


def send_request(request_id):

    client_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    start_time = time.time()

    try:

        client_socket.connect(
            (HOST, PORT)
        )

        message = f"Request {request_id}"

        client_socket.sendall(
            message.encode()
        )

        response = client_socket.recv(
            4096
        )

        end_time = time.time()

        latency = (
            end_time - start_time
        ) * 1000

        print(
            f"Request {request_id}: "
            f"{response.decode()} | "
            f"Latency: {latency:.2f} ms"
        )

    except Exception as e:

        print(
            f"Request {request_id} failed: {e}"
        )

    finally:

        client_socket.close()


if __name__ == "__main__":

    # ------------------------------------------
    # NUMBER OF REQUESTS
    # ------------------------------------------

    if len(sys.argv) > 1:

        number_of_requests = int(
            sys.argv[1]
        )

    else:

        number_of_requests = 10


    print(
        f"Starting load test with "
        f"{number_of_requests} requests..."
    )


    # ------------------------------------------
    # CREATE THREADS
    # ------------------------------------------

    threads = []

    start_time = time.time()


    for request_id in range(
        1,
        number_of_requests + 1
    ):

        thread = threading.Thread(
            target=send_request,
            args=(request_id,)
        )

        threads.append(
            thread
        )

        thread.start()


    # ------------------------------------------
    # WAIT FOR ALL REQUESTS
    # ------------------------------------------

    for thread in threads:

        thread.join()


    end_time = time.time()


    total_time = (
        end_time - start_time
    ) * 1000


    # ------------------------------------------
    # SUMMARY
    # ------------------------------------------

    print(
        "\nAll requests completed."
    )

    print(
        f"Total test time: "
        f"{total_time:.2f} ms"
    )