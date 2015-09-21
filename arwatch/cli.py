"""Client
"""

import socket

from arwatch import read_stream


class Client:
    def __init__(self):
        pass


if __name__ == '__main__':
    # Create a socket (SOCK_STREAM means a TCP socket)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    data = "ab" * 1024

    try:
        sock.connect(("localhost", 9999))
        sock.sendall(bytes(data + "\n", "utf-8"))

        received = str(read_stream(sock.recv), "utf-8")
    finally:
        sock.close()

    print("Sent:     {}".format(data))
    print(len(received))
    print("Received: {}".format(received))