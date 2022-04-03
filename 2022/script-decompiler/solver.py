#!/usr/bin/python3

MULTIPLIERS_1 = [0x0049, 0x0061, 0x000d, 0x0029, 0x0043, 0x0065, 0x0059, 0x008b, 0x0047, 0x0053]
ADDERS_1 =      [0x1b39, 0x18df, 0x13eb, 0x11ef, 0x1145, 0x12df, 0x0dfd, 0x13af, 0x149f, 0x0fef, 0x0fb5]
TARGET_VALUE_1 = 0xb0ef

MULTIPLIERS_2 = [0x003b, 0x00b5, 0x007f, 0x00a3, 0x0067, 0x00a3, 0x0095, 0x00c1, 0x00d3, 0x0097]
ADDERS_2      = [0x0539, 0x0e75, 0x11fb, 0x1237, 0x125f, 0x107b, 0x1951, 0x1b47, 0x151f, 0x14b1, 0x13eb]
TARGET_VALUE_2 = 0xd4b9

# Find values of "a, b, c, ..." in equation "ax1 + bx2 + cx3 + ... + k = 0";
# where "xn" = password[n] + ADDERS[n]
def findConstants(ADDERS, MULTIPLIERS, TARGET_VALUE):
    retvals = []
    retvals.append((ADDERS[-1] - TARGET_VALUE) & 0xffff)
    mult = 1
    for index in range(9, -1, -1):
        mult *= MULTIPLIERS[index]
        mult &= 0xffff
        retvals.append(mult)
    return list(reversed(retvals))

# Given two sets of constants of the form "ax1 + bx2 + cx3 + ... + k = 0",
# Returns a new set of constants for "ap1 + bp2 + bp3 + ... + k = 0", where "pn"
# is a character in the password.
def combineConstants(constants1, constants2):
    lastConstant = constants1[-1] + constants2[-1]
    retvals = []

    for i in range(10):
        v = (constants1[i] + constants2[i]) & 0xffff
        retvals.append(v)
        lastConstant += constants1[i] * ADDERS_1[i] + constants2[i] * ADDERS_2[i]
        lastConstant &= 0xffff

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
    return total

def sumConstants(password, constants):
    total = constants[-1]
    for i in range(10):
        total += password[i] * constants[i]
        total &= 0xffff
    return total

def solve(constants):
    ASSUMED = 8
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
            return tryvals

    return -1

assert(getPasswordHash('ABC', ADDERS_1, MULTIPLIERS_1) == 0xa7da)
assert(getPasswordHash('ABC', ADDERS_2, MULTIPLIERS_2) == 0xc4fe)

constants1 = findConstants(ADDERS_1, MULTIPLIERS_1, TARGET_VALUE_1)
constants2 = findConstants(ADDERS_2, MULTIPLIERS_2, TARGET_VALUE_2)

constants = combineConstants(constants1, constants2)

candidate = solve(constants)
print(hex(getPasswordHash(candidate, ADDERS_1, MULTIPLIERS_1)))

print([hex(x) for x in constants])
