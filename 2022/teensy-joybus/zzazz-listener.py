import serial, binascii, sys, time, struct
import socket
from server import *

# Constants
STATE_UNKNOWN = 0
STATE_LOGGING = 1

MAP_TO_SPOOF = 0x37130000

# Config
VERBOSE = False


# Variables
currentState = STATE_UNKNOWN

mapHandshake = [0xff1550be,0x1550beff,0x15000f00,0x37132220,0x00000000,0x02000000]
handshakeIndex = 0

numZeroPacketsReceived = 0
loadingMapID = 0

logString = ''


def logSend(data):
    global logString
    logString += 'SEND: ' + binascii.hexlify(data).decode() + '\n'
def logRecv(data):
    global logString
    logString += 'RECV: ' + binascii.hexlify(data).decode() + '\n'

# Server is sending data, return data to send to gameboy
def handleSend(data):
    global currentState
    if data[0] == 0x15:
        logSend(data[1:])
        if VERBOSE:
            print('SEND: ' + binascii.hexlify(data[1:]).decode())
    return data


# Gameboy is sending data, return data to send to server
def handleRecv(resp):
    global currentState, handshakeIndex, loadingMapID, logString, numZeroPacketsReceived, MAP_TO_SPOOF

    # Print GBA response
    if len(resp) > 1:
        if VERBOSE:
            print('RECV: ' + binascii.hexlify(resp[0:4]).decode())
        param = struct.unpack('>I', resp[0:4])[0]

        if currentState == STATE_UNKNOWN:
            if param == mapHandshake[0]:
                currentState = STATE_LOGGING
                handshakeIndex = 1
        elif currentState == STATE_LOGGING:
            if handshakeIndex == 5:
                # Modify the map we're moving to
                if MAP_TO_SPOOF == -1:
                    print('LOADING MAP: ' + hex(param >> 16) + ' POS: ' + hex(param & 0xffff))
                    loadingMapID = param
                else:
                    print('SPOOFING TO MAP: ' + hex(MAP_TO_SPOOF >> 16) + ' (POS: ' + hex(param & 0xffff) + ')')
                    resp = binascii.unhexlify(hex(MAP_TO_SPOOF)[2:])
                    loadingMapID = -1 # Don't save log for faked traffic
                    MAP_TO_SPOOF = -1

            handshakeIndex += 1

            if param == 0:
                numZeroPacketsReceived += 1
                if numZeroPacketsReceived >= 10:
                    print('WRITE')
                    if loadingMapID != -1:
                        f = open('traffic/' + hex(loadingMapID), 'w')
                        f.write(logString)
                        f.close()
                        loadingMapID = -1
                    currentState = STATE_UNKNOWN
                    logString = ''
            else:
                numZeroPacketsReceived = 0

        if not (logString == '' and param == 0):
            logRecv(resp)
    return resp


runServer(handleSend, handleRecv)
