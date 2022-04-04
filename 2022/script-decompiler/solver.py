#!/usr/bin/python3
import binascii

MULTIPLIERS_1 = [0x0049, 0x0061, 0x000d, 0x0029, 0x0043, 0x0065, 0x0059, 0x008b, 0x0047, 0x0053]
ADDERS_1 =      [0x1b39, 0x18df, 0x13eb, 0x11ef, 0x1145, 0x12df, 0x0dfd, 0x13af, 0x149f, 0x0fef, 0x0fb5]

MULTIPLIERS_2 = [0x003b, 0x00b5, 0x007f, 0x00a3, 0x0067, 0x00a3, 0x0095, 0x00c1, 0x00d3, 0x0097]
ADDERS_2      = [0x0539, 0x0e75, 0x11fb, 0x1237, 0x125f, 0x107b, 0x1951, 0x1b47, 0x151f, 0x14b1, 0x13eb]

# True values
TARGET_VALUE_1 = 0xb0ef
TARGET_VALUE_2 = 0xd4b9


def prime_factors(n):
    i = 2
    factors = []
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
            factors.append(i)
    if n > 1:
        factors.append(n)
    return factors

def factorizeConstants(constants):
    for i in range(10):
        print(prime_factors(constants[i]))

# Find values of "a, b, c, ..." in equation "ap1 + bp2 + cp3 + ... + k = 0";
# where "pn" = password[n]
def findConstants(ADDERS, MULTIPLIERS, TARGET_VALUE):
    lastConstant = (ADDERS[-1] - TARGET_VALUE) & 0xffff
    retvals = []
    mult = 1
    for index in range(9, -1, -1):
        mult *= MULTIPLIERS[index]
        mult &= 0xffff
        retvals.append(mult)
        lastConstant += mult * ADDERS[index]
        lastConstant &= 0xffff
    retvals = list(reversed(retvals))
    retvals.append(lastConstant)
    return retvals

def strToBytes(password):
    output = bytearray()
    for c in password:
        c = ord(c)
        assert(c >= ord('A') and c <= ord('Z'))
        output.append(c - ord('A') + 0xbb)
    while len(output) < 10:
        output.append(0xff)
    return output

# Get one of the two hashes for a password
def getPasswordHash(password, ADDERS, MULTIPLIERS):
    if type(password) is str:
        password = strToBytes(password)
    total = 0
    for i in range(10):
        total += ADDERS[i]
        total += password[i]
        total *= MULTIPLIERS[i]
        total &= 0xffff

    total += ADDERS[-1]
    total &= 0xffff
    return total

def sumConstants(password, constants):
    total = constants[-1]
    for i in range(10):
        total += password[i] * constants[i]
        total &= 0xffff
    return total

def solveSingleEquation(constants):
    ASSUMED = 1
    password_base = bytearray([0xbb] * ASSUMED)
    total = constants[-1]
    retvals = []

    for val in range(0, pow(256, 10 - ASSUMED)):
        tryvals = password_base[:]
        v = val
        for j in range(ASSUMED, 10):
            n = v & 0xff
            v >>= 8
            tryvals.append(n)

        if sumConstants(tryvals, constants) == 0:
            yield tryvals


tried = 0
password = []

def solveBothEquations(start=0):
    global tried

    #print('FRESH START')

    #assert(getPasswordHash(password, ADDERS_1, MULTIPLIERS_1) == TARGET_VALUE_1)
    for n1 in range(start, 10):
        p1L = password[n1]
        for p1N in range(0, 256):
            if p1N == p1L:
                continue

            for n2 in range(n1 + 1, 10):
                p2L = password[n2]
                c1 = constants1[n1]
                c2 = constants1[n2]

                diff1 = c1 * (p1N - p1L)
                if (diff1 % c2) != 0:
                    continue
                p2N = (-diff1 // c2 + p2L) & 0xffff
                if p2N < 0 or p2N >= 256:
                    continue
                diff2 = c2 * (p2N - p2L)
                #print('DIFF1: ' + hex(diff1))
                #print('DIFF2: ' + hex(diff2))
                password[n1] = p1N
                password[n2] = p2N

                #assert(getPasswordHash(password, ADDERS_1, MULTIPLIERS_1) == TARGET_VALUE_1)

                if sumConstants(password, constants2) == 0:
                    print('SOLUTION: ' + binascii.hexlify(password).decode())

                tried += 1
                if tried % 50 == 0:
                    print('Tried ' + str(tried) + ' values')

                solveBothEquations(n1 + 1)
                password[n1] = p1L
                password[n2] = p2L
                break


assert(getPasswordHash('ABC', ADDERS_1, MULTIPLIERS_1) == 0xa7da)
assert(getPasswordHash('ABC', ADDERS_2, MULTIPLIERS_2) == 0xc4fe)

constants1 = findConstants(ADDERS_1, MULTIPLIERS_1, TARGET_VALUE_1)
constants2 = findConstants(ADDERS_2, MULTIPLIERS_2, TARGET_VALUE_2)

assert(getPasswordHash(next(solveSingleEquation(constants1)), ADDERS_1, MULTIPLIERS_1) == TARGET_VALUE_1)
assert(getPasswordHash(next(solveSingleEquation(constants2)), ADDERS_2, MULTIPLIERS_2) == TARGET_VALUE_2)

#print([hex(x) for x in constants1])
#print([str(x) for x in constants2])
#print(factorizeConstants(constants1))

# This is really wack, I should only need to call "solveSingleEquation" once to
# get an initial setup value, but I'm lazy and my code in "solveBothEquations"
# is bad, so whatever
for p in solveSingleEquation(constants1):
    password = p
    solveBothEquations()


#takenValues = [0] * 65536
#takenCount = 0
#for i in range(65536):
#    passwd = [0] * 10
#    passwd[4] = i
#    h = getPasswordHash(passwd, ADDERS_1, MULTIPLIERS_1)
#    if not takenValues[h]:
#        takenValues[h] = 1
#        takenCount += 1
#print(takenCount)
