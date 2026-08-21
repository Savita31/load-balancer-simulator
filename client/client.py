import socket
import sys
import time


def send_request(
    host="127.0.0.1",
    port=9000,
    message="Hello"
):

    client_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    start_time = time.time()

    try:
        client_socket.connect(
            (host, port)
        )

        client_socket.sendall(
            message.encode()
        )

        response = client_socket.recv(4096)

        end_time = time.time()

        print(f"Response: {response.decode()}")

        print(
            f"Latency: "
            f"{(end_time - start_time) * 1000:.2f} ms"
        )

    except Exception as e:

        print(f"Client error: {e}")

    finally:

        client_socket.close()


if __name__ == "__main__":

    message = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "Hello Load Balancer"
    )

    send_request(message=message)