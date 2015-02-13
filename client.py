import socket
import time
import sys

# class WFConnector:

# host = '192.168.12.12'
# port = 8008
#
# s = None
# for res in socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM):
#     family, socket_type, proto, canonname, socket_address = res
#     try:
#         s = socket.socket(family, socket_type, proto)
#     except socket.error:
#         s = None
#         continue
#     try:
#         s.connect(socket_address)
#     except socket.error:
#         s.close()
#         s = None
#         continue
#     break
# if s is None:
#     print('could not open socket')
#
# while 1:
#
#     dataToBeSent = str.encode(input("Input string: "))
#     s.sendall(dataToBeSent)
#
#     data = s.recv(1024)
#     print('Received', repr(data))
# s.close()


class Connector:
    def __init__(self):
        self.socket = None
        self.connected = False
        self.connect()

    def connect(self):
        host = '192.168.12.12'
        port = 8008
        for res in socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM):
            family, socket_type, proto, canonname, socket_address = res
            try:
                s = socket.socket(family, socket_type, proto)
            except socket.error:
                continue
            try:
                s.connect(socket_address)
            except socket.error:
                s.close()
                continue
            s.setblocking(False)
            self.socket = s
            print("[Info] Connection established.")
            print("         family: ", family)
            print("         socket_type: ", socket_type)
            print("         proto: ", proto)
            break
        if not self.socket:
            print("[Error] Unable to establish connection.")
        else:
            self.connected = True

    def send(self, msg):
        if not self.connected:
            self.connect()
        if self.connected:
            print("[Info] Sending message: ", msg)
            self.socket.sendall(str.encode(msg))
        else:
            print("[Error] Unable to send message. Connection loss.")

    def receive(self):
        if not self.connected:
            self.connect()
        if self.connected:
            msg = self.socket.recv(1024)
            if msg:
                print("[Info] Received: ", msg)
            return msg
        else:
            print("[Error] Unable to receive message. Connection loss.")


connector = Connector()
while True:
    dataToBeSent = input("Input string: ")
    connector.send(dataToBeSent)
    connector.receive()