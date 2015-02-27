# 2015 MDP Grp12 by Wenjie

# import for multi-threading
import threading

from bluetooth import *

# import for wifi socket
import socket

# import for arduino usb serial
import serial

import queue

import sys

import time


####################################################################################################
# Bluetooth server
# reference: http://homepages.ius.edu/RWISMAN/C490/html/PythonandBluetooth.htm
# Construct a socket for COMM service.

# def connectBT():
#     global btBuff, wfBuff, serBuff, btSocket, wfSocket, serSocket, btLock, wfLock, serLock, btConnected, wfConnected, serConnected
#     print "[BT] COMM socket constructed"
#     server_socket = BluetoothSocket(RFCOMM)
#
#     #Server binds the script on host to port 4
#     print "[BT] Bind script to port 4"
#     server_socket.bind(("", 4))
#
#     #Server listens to accept 1 connection at a time
#     print "[BT] Server starts listening "
#     server_socket.listen(1)
#
#     advertise_service( server_socket, "SampleServer",
#                         service_classes = [ bluetooth.SERIAL_PORT_CLASS ],
#                         profiles = [ bluetooth.SERIAL_PORT_PROFILE ],
#                 )
#
#     #Server accepts connection request from a client
#     #Client_socket is the socket used for communication with client and address the client's address
#
#     btSocket, address = server_socket.accept()
#     print "[BT] Connection accepted"
#     print "[BT] Connect by: ", address
#     if (btSocket != ""):
#         btConnected = True
#         del btBuff[:]
#         del wfBuff[:]
#         del serBuff[:]


# def receiveBT():
#     global btBuff, wfBuff, serBuff, btSocket, wfSocket, serSocket, btLock, wfLock, serLock, btConnected, wfConnected, serConnected
#
#     while (1):
#
#         try:
#             while (btConnected == False):
#                 print "debug point 6"
#                 connectBT()
#
#             if (btConnected == True):
#                 while(1):
#                     print "[BT] ", btSocket
#                     #Receive data through socket server_socket, assign to variable data; a maximum of 1024 characters received at a time.
#                     btDataReceived = btSocket.recv(1024)
#                     print "[BT] Bluetooth received: " + btDataReceived
#
#                     if (btDataReceived[0] == "A" or btDataReceived[0] == "a") and serConnected == True:
#                         serLock.acquire()
#                         serBuff.append(btDataReceived[1:])
#                         serLock.release()
#                         print "[BT] Now serBuff is ", serBuff
#                     elif (btDataReceived[0] == "P" or btDataReceived[0] == "p") and wfConnected == True:
#                         wfLock.acquire()
#                         wfBuff.append(btDataReceived[1:])
#                         wfLock.release()
#                         print "[BT] Now wtBuff is ", wfBuff
#                     else:
#                         print "[BT] Undefined received data from bluetooth "
#         #if client side reset the connection, we will through the exception, close the current socket and reset the bt server.
#         #same method apply to the rest communication channels
#         except Exception, e:
#             print "[BT] exception: ", e
#             if btSocket!= '':
#                 btSocket.close()
#             btConnected = False


# def send_bt():
#     while 1:
#         try:
#             while not bt_connected:
#                 pass
#
#             if (btConnected == True):
#                 print("[BT] Ready to send data to bluetooth dev ")
#                 while (1):
#                     while (btBuff != []):
#                         btDataSend = btBuff.pop()
#
#                         btLock.acquire()
#                         btSocket.send(btDataSend)
#                         btLock.release()
#                         print("[BT] Send [" + btDataSend + "] to N7 via bluetooth")
#         except Exception:
#             print("[BT] exception: ", sys.exc_info())
#             if btSocket!= '':
#                 btSocket.close()
#             btConnected = False


####################################################################################################
# Wifi server
# reference: https://docs.python.org/2/library/socket.html


class WFConnector:
    def __init__(self):
        host = '192.168.12.12'
        port = 8008
        family = socket.AF_INET
        socket_type = socket.SOCK_STREAM

        self.server_socket = socket.socket(family, socket_type)

        # set the wf address reusable
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        print("[WF] WF Binds to host " + host + ", PORT: " + str(port))
        self.server_socket.bind((host, port))

        print("[WF] WF Server starts listening ")
        self.server_socket.listen(1)

        self.client_socket = None

        self.connected = False

    def connect(self):

        try:
            self.client_socket, address = self.server_socket.accept()
            print("[WF] WF Connection accepted")
            print("[WF] Connected by", address)

            self.connected = True

        except Exception:
            print("[Error] Unable to connect wifi.")
            print(sys.exc_info())
            time.sleep(1)


class SEConnector:
    def __init__(self):
        self.connected = False
        self.serial = None

    def connect(self):
        # #Clear all buffer
        # del btBuff[:]
        # del wfBuff[:]
        # del serBuff[:]
        try:
            self.serial = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
            self.serial.write(str.encode("i"))
        except Exception:
            try:
                self.serial = serial.Serial('/dev/ttyACM1', 9600, timeout=1)
            except Exception:
                print("[Error] Unable to connect serial port.")
                print(sys.exc_info())
                return
        time.sleep(2)
        self.connected = True


class BTConnector:
    def __init__(self):
        self.connected = False
        self.client_socket = None
        self.server_socket = None

    def connect(self):
        # Creating the server socket and bind to port
        btport = 4
        try:
            self.server_socket = BluetoothSocket( RFCOMM )
            self.server_socket.bind(("", btport))
            self.server_socket.listen(1)	# Listen for requests
            self.port = self.server_socket.getsockname()[1]
            uuid = "00001101-0000-1000-8000-00805F9B34FB"

            advertise_service( self.server_socket, "SampleServer",
                               service_id = uuid,
                               service_classes = [ uuid, SERIAL_PORT_CLASS ],
                               profiles = [ SERIAL_PORT_PROFILE ],
                                )
            print("Waiting for connection on RFCOMM channel %d" % self.port)
            # Accept requests
            self.client_socket, client_address = self.server_socket.accept()
            print("Accepted connection from ", client_address)
            self.connected = True

        except Exception:
            print("Error address already in use")
            self.close_bt_socket()
            self.connect()


class Server:
    def __init__(self):
        self.wf = WFConnector()
        self.se = SEConnector()
        self.bt = BTConnector()
        self.wf_buffer = queue.Queue()
        self.se_buffer = queue.Queue()
        self.bt_buffer = queue.Queue()

    def receive_wf(self):
        while True:
            # print("[Thread] ", threading.current_thread())
            try:
                while not self.wf.connected:
                    self.wf.connect()
                while True:
                    data_received = self.wf.client_socket.recv(1024)
                    if data_received:
                        print("[WF] Wifi received: " + data_received.decode())
                        self.se_buffer.put(data_received.decode())
                        # For wifi testing
                        # self.wf_buffer.put("Receipt from RPi: " + data_received.decode())
                        # self.wf_buffer.put("Second receipt from Rpi: " + data_received.decode())
                        # self.wf_buffer.put("Third receipt from Rpi: " + data_received.decode())

            except Exception:
                print("[Error] Wifi connection loss.")
                print(sys.exc_info())
                if not self.wf.client_socket:
                    self.wf.client_socket.close()
                self.wf.wf_connected = False
                time.sleep(1)

    def receive_se(self):
        while True:
            # print("[Thread] ", threading.current_thread())
            try:
                while not self.se.connected:
                    self.se.connect()
                while True:
                    data_received = self.se.serial.readline()
                    if data_received:
                        data_decoded = data_received.decode()
                        print("[SE] Serial received: " + data_decoded)
                        if '[Sensor] ' in data_decoded:
                            data_to_send = data_decoded[9:]
                            self.wf_buffer.put(data_to_send)

            except Exception:
                print("[Error] Serial port connection loss.")
                print(sys.exc_info())
                self.se.connected = False
                time.sleep(1)

    def receive_bt(self):
        while True:
            try:
                while not self.bt.connected:
                    self.bt.connect()
                while True:
                    data_received = self.bt.client_socket.recv(1024)
                    print("[BT] Bluetooth received: " + data_received)
            except Exception:
                print("[Error] Bluetooth connection loss.")
                print(sys.exc_info())
                self.bt.connected = False
                # self.bt.connect()	# Reestablish connection

    def send_wf(self):
        if not self.wf.connected:
            return
        else:
            while self.wf_buffer.qsize():
                print("[WF] Ready to send data to PC.")
                try:
                    data_to_send = self.wf_buffer.get()
                    print("[WF] Sending to PC: ", data_to_send)
                    self.wf.client_socket.sendall(str.encode(data_to_send))
                except Exception:
                    print("[Error] Unable to send data through Wifi. Connection loss.")
                    print(sys.exc_info())
                    if not self.wf.client_socket:
                        self.wf.client_socket.close()
                    self.wf.connected = False

    def send_se(self):
        if not self.se.connected:
            return
        else:
            while self.se_buffer.qsize():
                print("[SE] Ready to send data to Arduino.")
                try:
                    data_to_send = self.se_buffer.get()
                    print("[SE] Sending to Arduino: ", data_to_send)
                    self.se.serial.write(str.encode(data_to_send))
                except Exception:
                    print("[Error] Unable to send data through Serial Port. Connection loss.")
                    print(sys.exc_info())
                    self.se.connected = False
                    # self.se_buffer.put(data_to_send)

    def send_bt(self):
        if not server.bt.connected:
            return
        else:
            while server.bt_buffer.qsize():
                print("[BT] Ready to send data to Android N7.")
            try:
                data_to_send = self.bt_buffer.get()
                print("[BT] Sending to Android N7: ", data_to_send)
                self.bt.client_socket.send(str.encode(data_to_send))
            except Exception:
                print("[Error] Unable to send data through Bluetooth. Connection loss.")
                print(sys.exc_info())
                server.bt.connected = False
                # self.bt.connect()	# Reestablish connection


####################################################################################################

server = Server()

# wf_receiver_thread = threading.Thread(name="Wifi Receiver", target=server.receive_wf)
# se_receiver_thread = threading.Thread(name="Serial Receiver", target=server.receive_se)
bt_receiver_thread = threading.Thread(name="Bluetooth Receiver", target=server.receive_bt)

# wf_receiver_thread.start()
# se_receiver_thread.start()
bt_receiver_thread.start()


while True:
    i = input("Msg to send:")
    server.bt_buffer.put(i)
    # print("[Thread] ", threading.current_thread())
    # server.send_se()
    # server.send_wf()
    server.send_bt()
    time.sleep(0)
