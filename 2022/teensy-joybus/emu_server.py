# mitm for emulator joybus

import serial, binascii, sys, time
import socket

SERVER_IP = '127.0.0.1'
DATA_PORT = 54970
CLOCK_PORT = 49420

LISTEN_DATA_PORT = 54971 # Modify mGBA's source to use these alternate ports
LISTEN_CLOCK_PORT = 49421


def runServer(handleSend, handleRecv):
    mgba_data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mgba_data_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    mgba_data_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    mgba_data_sock.setblocking(1)
    mgba_data_sock.bind((SERVER_IP, LISTEN_DATA_PORT))
    mgba_data_sock.listen()

    mgba_clock_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mgba_clock_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    mgba_clock_sock.bind((SERVER_IP, LISTEN_CLOCK_PORT))
    mgba_clock_sock.listen()

    (mgba_data_conn, _) = mgba_data_sock.accept()
    (mgba_clock_conn, _) = mgba_clock_sock.accept()

    print('mGBA connected.')

    server_data_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_data_conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    server_data_conn.connect((SERVER_IP, DATA_PORT))
    server_data_conn.setblocking(1)

    server_clock_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_clock_conn.connect((SERVER_IP, CLOCK_PORT))

    print('Connected to server.')

    while True:
        data = server_data_conn.recv(5)
        clocks = server_clock_conn.recv(4)

        data = handleSend(data)
        mgba_data_conn.send(data)
        mgba_clock_conn.send(clocks)
        resp = mgba_data_conn.recv(5)
        resp = handleRecv(resp)
        server_data_conn.send(resp)
