# 2015 MDP Grp12 by Wenjie

# import for multi-threading
import threading

# import for bluetooth
# from bluetooth import *

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
        self.connected = False
        self.socket = None

    def connect(self):
        host = '192.168.12.12'     # Symbolic name meaning all available interfaces
        port = 8008              # Arbitrary non-privileged port

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # set the wf address reusable
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            print("[WF] WF Binds to host " + str(host) + ", PORT: " + str(port))
            s.bind((host, port))

            print("[WF] WF Server starts listening ")
            s.listen(1)

            self.socket, addr = s.accept()
            print("[WF] WF Connection accepted")
            print("[WF] Connected by", addr)

            if self.socket:
                self.connected = True
        except Exception:
            print("[Error] Unable to connect wifi.", sys.exc_info())
            # del btBuff[:]
            # del wfBuff[:]
            # del serBuff[:]


class SEConnector:
    def __init__(self):
        self.connected = False
        self.socket = None

    def connect(self):
        # #Clear all buffer
        # del btBuff[:]
        # del wfBuff[:]
        # del serBuff[:]
        try:
            self.socket = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
            time.sleep(2)
            self.socket.write(str.encode("i"))
        except Exception:
            try:
                self.socket = serial.Serial('/dev/ttyACM1', 9600, timeout=1)
                time.sleep(2)
            except Exception:
                print("[Error] Unable to connect serial port.")
                return
        self.connected = True


class Server:
    def __init__(self):
        self.wf = WFConnector()
        self.se = SEConnector()
        self.wf_buffer = queue.Queue()
        self.se_buffer = queue.Queue()
        self.se_buffer.put("i")

    def receive_wf(self):
        while True:
            # print("[Thread] ", threading.current_thread())
            try:
                while not self.wf.connected:
                    self.wf.connect()
                while True:
                    data_received = self.wf.socket.recv(1024)
                    if data_received:
                        print("[WF] Wifi received: " + data_received.decode())
                        self.se_buffer.put(data_received.decode())
                        self.wf_buffer.put("Receipt from RPi: " + data_received.decode())
                    # if (wfDataReceived[0] == "A" or wfDataReceived[0] == "a") and serConnected == True:
                    #     serLock.acquire()
                    #     serBuff.append(wfDataReceived[1:])
                    #     print("[WF] serBuff now is ", serBuff)
                    #     serLock.release()
                    # elif (wfDataReceived[0] == "N" or wfDataReceived[0] == "n") and btConnected == True:
                    #     btLock.acquire()
                    #     btBuff.append(wfDataReceived[1:])
                    #     print("[WF] btBuff now is ", btBuff)
                    #     btLock.release()

                    # else:
                    #     print("[WF] Undefined received data from wifi")
            except Exception:
                print("[WF] exception: ", sys.exc_info())
                if not self.wf.socket:
                    self.wf.socket.close()
                self.wf.wf_connected = False

    def receive_se(self):
        while True:
            # print("[Thread] ", threading.current_thread())
            try:
                while not self.se.connected:
                    self.se.connect()
                while True:
                    data_received = self.se.socket.readline()
                    if data_received:
                        print("[SE] Serial received: " + data_received.decode())
                    self.wf_buffer.put(data_received.decode())

                    # if (serDataReceived[0] == "N" or serDataReceived[0] == "n") and btConnected == True:
                    #     btLock.acquire()
                    #     btBuff.append(serDataReceived[1:])
                    #     btLock.release()
                    #     print "[SER] Now btBuff is ", btBuff
                    # elif (serDataReceived[0] == "P" or serDataReceived[0] == "p") and wfConnected == True:
                    #     serDataReceived = 'a' + serDataReceived[1:]
                    #     wfLock.acquire()
                    #     wfBuff.append(serDataReceived)
                    #     wfLock.release()
                    #     print "[SER] Now wtBuff is ", wfBuff
                    # else:
                    #     print "[SER] Undefined received data from Arduino"
            except Exception:
                print("[SE] exception: ", sys.exc_info())
                if self.se.socket:
                    self.se.socket.close()
                self.se.connected = False

    def send_wf(self):
        if not self.wf.connected:
            return
        else:
            while self.wf_buffer.qsize():
                print("[WF] Ready to send data to PC.")
                try:
                    data_to_send = self.wf_buffer.get()
                    print("[WF] Sending to PC: ", data_to_send)
                    self.wf.socket.sendall(str.encode(data_to_send))
                except Exception:
                    print("[Error] Unable to send data through Wifi. Resetting connection.")
                    print(sys.exc_info())
                    if not self.wf.socket:
                        self.wf.socket.close()
                    self.wf.connected = False
            # while True:
            #     while (wfBuff != []):
            #         wfDataSend = wfBuff.pop()
            #
            #         wfLock.acquire()
            #         wfSocket.sendall(wfDataSend)
            #         wfLock.release()
        #
        # except Exception, e:
        #     print "[WF] exception: ", e
        #     if wfSocket!= '':
        #         wfSocket.close()
        #     wfConnected = False

    def send_se(self):
        if not self.se.connected:
            return
        else:
            while self.se_buffer.qsize():
                print("[SE] Ready to send data to Arduino.")
                try:
                    data_to_send = self.se_buffer.get()
                    print("[SE] Sending to Arduino: ", data_to_send)
                    self.se.socket.write(str.encode(data_to_send))
                except Exception:
                    print("[Error] Unable to send data through Serial Port. Resetting connection.")
                    print(sys.exc_info())
                    if not self.se.socket:
                        self.se.socket.close()
                    self.se.connected = False
                    # self.se_buffer.put(data_to_send)

    # def send_data(self):
    #     while True:
    #         self.send_wf()
    #         self.send_se()
    #         time.sleep(0)

####################################################################################################

# declare buffers
# bt_buff = queue.Queue()
# se_buff = queue.Queue()

# declare sockets
# bt_socket = ""
# wf_socket = ""
# se_socket = ""

# declare flag
# bt_connected = False
# wf_connected = False
# se_connected = False


# bt_receiver = threading.Thread(name="BTReceiver", target="")
# wf_receiver_thread = threading.Thread(name="WFReceiver", target=connect_wf())
# se_receiver_thread = threading.Thread(name="SEReceiver", target=connect_ser())

server = Server()

wf_receiver_thread = threading.Thread(name="Wifi Receiver", target=server.receive_wf)
se_receiver_thread = threading.Thread(name="Serial Receiver", target=server.receive_se)

wf_receiver_thread.start()
se_receiver_thread.start()


while True:
    # print("[Thread] ", threading.current_thread())
    # server.send_wf()
    server.send_se()
    time.sleep(0)

# while True:
#     # server.send_se()
#     server.send_wf()
#     # server.receive_se()
#     server.receive_wf()


# while True:
#    send_ser()
#    send_wf()


####################################################################################################
#Arduino
#reference: http://www.elcojacobs.com/communicating-between-python-and-arduino-with-pyserial/
#to connect arduino via bluetooth we are using serial though I name it serSocket