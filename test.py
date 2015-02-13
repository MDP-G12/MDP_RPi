import serial
import time

socket = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(1)
print 'start to communicate'
socket.write("i")
while 1:
    data =  socket.readline()
    if len(data) == 0:
        print 'time_out'
    else:
        print data
        break
