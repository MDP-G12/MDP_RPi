import serial
import time


class SEConnector:
    def __init__(self):
        self.serial = None
        self.connected = False
        self.connect()

    def connect(self):
        try:
            self.serial = serial.Serial('/dev/ttyACM0', 9600, timeout=2)
            self.connected = True
        except Exception:
            try:
                self.serial = serial.Serial('/dev/ttyACM1', 9600, timeout=2)
                self.connected = True
            except Exception:
                print("[Error] Unable to connect. Reconnect in 2s.")
                time.sleep(2)
                self.connect()


s = SEConnector()

while 1:
    i = input("Input a command: ")
    try:
        s.serial.write(str.encode(i))
    except Exception:
        print("[Error] Failed to send command. Reconnect in 1s.")
        time.sleep(1)
        s.connect()
    else:
        try:
            print(s.serial.readline().decode())
        except Exception:
            print("[Error] Failed to send command. Reconnect in 1s.")
            time.sleep(1)
            s.connect()
