"""Daemon
"""

import socketserver

from arwatch import read_stream


class DaemonHandler(socketserver.BaseRequestHandler):

    def handle(self):
        # self.request is the TCP socket connected to the client

        self.data = read_stream(self.request.recv)

        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        print(len(self.data))
        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())


class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


if __name__ == "__main__":

    server = ThreadingTCPServer(("localhost", 9999), DaemonHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
