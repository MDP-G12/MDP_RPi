import socket
import time
import sys

host = '192.168.12.12'
port = 8008

s = None
for res in socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM):
    family, socket_type, proto, canonname, socket_address = res
    try:
        s = socket.socket(family, socket_type, proto)
    except socket.error:
        s = None
        continue
    try:
        s.connect(socket_address)
    except socket.error:
        s.close()
        s = None
        continue
    break
if s is None:
    print('could not open socket')

while 1:

    dataToBeSent = str.encode(input("Input string: "))
    s.sendall(dataToBeSent)

    data = s.recv(1024)
    print('Received', repr(data))
s.close()
