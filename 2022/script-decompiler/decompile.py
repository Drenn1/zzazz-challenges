#!/usr/bin/python3
import sys, struct

# Print hex value with set # of digits
def myhex(val, length=1):
    if val < 0:
        return "-" + myhex(-val, length)
    out = hex(val)[2:]
    while len(out) < length:
        out = '0' + out
    return out

def decodeScript(scriptData, baseAddr):
    pos = 0
    out = sys.stdout

    jumpAddressList = []

    def nextByte():
        nonlocal pos
        b = scriptData[pos]
        pos += 1
        return b
    def nextHalfWord():
        nonlocal pos
        w = struct.unpack('<H', scriptData[pos : pos + 2])[0]
        pos += 2
        return w
    def nextWord():
        nonlocal pos
        w = struct.unpack('<I', scriptData[pos : pos + 4])[0]
        pos += 4
        return w
    def printIndex(i):
        return '[data+' + myhex(i, 2) + ']'
    def printVar(v):
        return '[' + myhex(v, 4) + ']'
    def printCond(c):
        return 'COND:'+myhex(2)
    def printScriptAddr(a):
        jumpAddressList.append(a)
        return myhex(a, 8)
    def printStd(s):
        return myhex(s, 2)
    def writeLine(l, r=''):
        header = hex(opcodeAddr) + ': ' + l
        spaces = 38 - len(header)
        out.write(header + (' ' * spaces) + r + '\n')

    while True:
        opcodeAddr = baseAddr + pos
        cmd = nextByte()
        if cmd == 0:
            writeLine('nop')
        elif cmd == 0x02:
            writeLine('end')
            if not opcodeAddr+1 in jumpAddressList:
                return
        elif cmd == 0x03:
            writeLine('return')
            if not opcodeAddr+1 in jumpAddressList:
                return
        elif cmd == 0x04:
            func = nextWord()
            writeLine('call', printScriptAddr(func))
        elif cmd == 0x06:
            cond = nextByte()
            ptr = nextWord()
            writeLine('goto_if', printCond(cond) + ', ' + printScriptAddr(ptr))
        elif cmd == 0x09:
            index = nextByte()
            writeLine('callstd', printStd(index))
        elif cmd == 0x0f:
            index = nextByte()
            val = nextWord()
            writeLine('loadword', printIndex(index) + ' = ' + myhex(val, 8))
        elif cmd == 0x11:
            val = nextByte()
            ptr = nextWord()
            writeLine('setptr', myhex(ptr, 8) + ' = ' + myhex(val, 2))
        elif cmd == 0x12:
            index = nextByte()
            val = nextWord()
            writeLine('loadbytefromptr', printIndex(index) + ' = ' + printIndex(val))
        elif cmd == 0x13:
            index = nextByte()
            addr = nextWord()
            writeLine('setptrbyte', myhex(addr, 8) + ' = ' + printIndex(index))
        elif cmd == 0x16:
            var = nextHalfWord()
            val = nextHalfWord()
            writeLine('setvar', printVar(var) + ' = ' + myhex(val, 4))
        elif cmd == 0x17:
            var = nextHalfWord()
            val = nextHalfWord()
            writeLine('addvar', printVar(var) + ' += ' + myhex(val, 4))
        elif cmd == 0x18:
            var = nextHalfWord()
            val = nextHalfWord()
            writeLine('subvar', printVar(var) + ' -= ' + myhex(val, 4))
        elif cmd == 0x19:
            dest = nextHalfWord()
            src = nextHalfWord()
            writeLine('copyvar', printVar(dest) + ' = ' + printVar(src))
        elif cmd == 0x21:
            var = nextHalfWord()
            val = nextHalfWord()
            writeLine('compare_var_to_value', printVar(var) + ' == ' + myhex(val, 4))
        elif cmd == 0x23:
            func = nextWord()
            writeLine('callnative', myhex(func, 8))
        elif cmd == 0x27:
            writeLine('waitstate')
        elif cmd == 0x2f:
            se = nextHalfWord()
            writeLine('playse', myhex(se, 4))
        elif cmd == 0x6c:
            writeLine('release')
        else:
            out.write('UNKNOWN OPCODE ' + myhex(cmd, 2) + '\n')
            return


SCRIPT_ADDR = 0x00182b7 # Top-level script

f = open('cracker3_memdump_02000000.bin', 'rb')
memdump = f.read()
f.close()

scriptBytes = memdump[SCRIPT_ADDR:]


decodeScript(scriptBytes, 0x02000000 + SCRIPT_ADDR)
