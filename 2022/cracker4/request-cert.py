#!/usr/bin/python3
import binascii, base64, requests, time

# Grab this from mitmproxy observation of a conversation with the client
SESSION_TOKEN='INSERT_TOKEN_HERE'

def sendPostRequest(data):
    headers={'X-Foolssessiontoken': SESSION_TOKEN}
    r = requests.post('https://fools2022.online/packet/5455720', data=data, headers=headers)
    return r

def buildRequest(holder, typ):
    data = bytearray()
    data.extend(binascii.unhexlify('07000000'))
    string = 'holder=' + holder + '/type=' + typ
    data.extend(string.encode())
    data.append(0xff)
    while len(data) % 4 != 0:
        data.append(0x00)
    data.extend(binascii.unhexlify('08000000'))
    return base64.b64encode(data)

def requestCert(holder):
    req = buildRequest(holder, 'silver')
    print('REQUESTING CERT: ' + str(base64.b64decode(req)[4:]))
    r = sendPostRequest(req)
    if r.ok:
        return base64.b64decode(base64.b64decode(r.text))
    else:
        print(r)

def appraiseCert(cert):
    data = bytearray()
    data.extend(binascii.unhexlify('08000000'))
    data.extend(base64.b64encode(cert))
    data.append(0xff)
    while len(data) < 0x104:
        data.append(0)
    assert(len(data) == 0x104)
    r = sendPostRequest(base64.b64encode(data))
    if r.ok:
        return base64.b64decode(r.text)
    else:
        print(base64.b64encode(data))
        print(r)

BLOCK_SIZE = 16

# This won't work 100% of the time because the length of the "serial" parameter
# may change, but it usually works.
cert = bytearray(requestCert('AAAAAAAAAAAAAAAABBBBBBBBBBBBBBBBBBBB'))

if not cert is None:
    assert(len(cert) % BLOCK_SIZE == 0)
    #for i in range(0, len(cert), BLOCK_SIZE):
    #    print(binascii.hexlify(cert[i : i + BLOCK_SIZE]).decode())

    time.sleep(1)

    target_string = b'/type=gold\xff'

    for i in range(len(target_string)):
        # Replace "B" characters in the name with the desired values using
        # a "bit-flipping" attack.
        # This will scramble half of the name, but that's fine.
        pos = 48 + i
        cert[pos] ^= target_string[i] ^ ord('B')

    data = appraiseCert(cert)
    if not data is None:
        print('APPRAISED CERT: ' + str(data[4:]))
