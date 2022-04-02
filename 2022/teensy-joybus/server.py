import serial, binascii, sys, time
import socket

SERIAL_DEVICE = '/dev/ttyACM0'
DOLPHIN_IP = '127.0.0.1'
DATA_PORT = 54970
CLOCK_PORT = 49420


serial_device = serial.Serial(SERIAL_DEVICE, baudrate=115200)
if serial_device == None:
    print('Error opening serial device.')
    sys.exit(1)

def readFromSerial():
    while True:
        data = serial_device.read(1)
        if data[0] == 1: # MSG
            l = serial_device.read(1)[0]
            msg = serial_device.read(l).decode()
            print('TEENSY: ' + msg)
        else:
            return data[0]

def readFromSerial2(l):
    data = bytearray()
    while len(data) < l:
        data.extend(serial_device.read(l - len(data)))
    return data


def runServer(handleSend, handleRecv):
    data_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    data_conn.connect((DOLPHIN_IP, DATA_PORT))
    data_conn.setblocking(1)

    clock_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clock_conn.connect((DOLPHIN_IP, CLOCK_PORT))

    flip = 0
    count = 0

    while True:
        data = data_conn.recv(5)
        clock_conn.recv(4) # Ignore the clock data

        serial_device.write(handleSend(data))
        cmd = readFromSerial()
        if cmd == 2: # SEND_DATA
            l = serial_device.read(1)[0]
            resp = readFromSerial2(l)
            data_conn.send(handleRecv(resp))
        elif cmd == 3: # NO_RESPONSE
            print('NO RESPONSE')
            pass
        else:
            print('UNKNOWN CMD: ' + hex(cmd))
