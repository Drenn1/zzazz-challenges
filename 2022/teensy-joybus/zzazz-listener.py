import serial, binascii, sys, time, struct, os, socket
from datetime import datetime
from server import *

MAP_TO_SPOOF = -1

CMD_NONE = 0x00
CMD_LOAD_MAP = 0x02

# Config
VERBOSE = False


# Variables
currentCmd = CMD_NONE

mapHandshake = [0xff1550be,0x1550beff,0x15000f00,0x37132220,0x00000000,0x02000000]
handshakeIndex = 0

numZeroPacketsReceived = 0
loadingMapDword = 0

logString = ''


# Print hex value with set # of digits
def myhex(val, length=1):
    if val < 0:
        return "-" + myhex(-val, length)
    out = hex(val)[2:]
    while len(out) < length:
        out = '0' + out
    return out

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

def mapIDFromMapDword(dword):
    return (dword >> 24) | ((dword >> 8) & 0xff00)

# Gameboy is sending data, return data to send to server
def handleRecv(resp):
    global currentState, handshakeIndex, loadingMapDword, logString, numZeroPacketsReceived, MAP_TO_SPOOF, currentCmd

    # Print GBA response
    if len(resp) > 1:
        if VERBOSE:
            print('RECV: ' + binascii.hexlify(resp[0:4]).decode())
        param = struct.unpack('>I', resp[0:4])[0]

        if currentCmd == CMD_NONE:
            if handshakeIndex >= 2:
                currentCmd = resp[0]
                if currentCmd != CMD_NONE:
                    print('CMD ' + hex(currentCmd))
                    handshakeIndex = 1
            elif param == mapHandshake[handshakeIndex]:
                handshakeIndex += 1
            else:
                handshakeIndex = 0
        else:
            if currentCmd == CMD_LOAD_MAP and handshakeIndex == 2:
                # Modify the map we're moving to
                if MAP_TO_SPOOF == -1:
                    print('LOADING MAP: ' + myhex(mapIDFromMapDword(param), 4) + ' POS: ' + myhex(param & 0xffff, 4))
                    loadingMapDword = param
                else:
                    print('SPOOFING TO MAP: ' + myhex(MAP_TO_SPOOF, 4) + ' POS: ' + myhex(param & 0xffff, 4))
                    resp = bytearray([MAP_TO_SPOOF & 0xff, MAP_TO_SPOOF >> 8])
                    resp.extend(binascii.unhexlify(myhex(param & 0xffff, 4)))
                    loadingMapDword = -1 # Don't save log for faked traffic
                    MAP_TO_SPOOF = -1

            handshakeIndex += 1

            if param == 0:
                numZeroPacketsReceived += 1
                if numZeroPacketsReceived >= 10:
                    destFilename = ''
                    if currentCmd == CMD_LOAD_MAP:
                        if loadingMapDword != -1:
                            mapID = mapIDFromMapDword(loadingMapDword)
                            mapPos = loadingMapDword & 0xffff
                            destFilename = 'traffic/map/' + myhex(mapID, 4) + '-' + myhex(mapPos, 4)
                            loadingMapDword = -1
                    else:
                        directory = 'traffic/cmd' + myhex(currentCmd, 2)
                        if not os.path.exists(directory):
                            os.mkdir(directory)
                        destFilename = directory + '/' + str(int(time.time()))

                    if destFilename != '':
                        # Ensure file being written to doesn't exist
                        extension = 0
                        uniqueDestFilename = destFilename
                        while os.path.exists(uniqueDestFilename):
                            uniqueDestFilename = destFilename + '.' + str(extension)
                            extension += 1

                        print('WRITE TO ' + uniqueDestFilename)
                        f = open(uniqueDestFilename, 'w')
                        f.write('TIME: ' + str(datetime.now()) + '\n\n')
                        f.write(logString)
                        f.close()
                        currentCmd = CMD_NONE
                        logString = ''
            else:
                numZeroPacketsReceived = 0

        if not (logString == '' and param == 0):
            logRecv(resp)
    return resp


runServer(handleSend, handleRecv)
