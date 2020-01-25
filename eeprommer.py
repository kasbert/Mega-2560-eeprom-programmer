#!/usr/bin/env python2.7
# Uses the Arduino firmware given on http://danceswithferrets.org/geekblog/?p=496
#
# -b size (in decimal)              - blank eeprom with 0xff
# -r start end (in decimal)         - read eeprom to terminal
# -s file.bin (programming)         - program eeprom with file.bin
# -v file.bin (verify content)      - program eeprom with file.bin
# -S file.bin ('smart' programming) - smart programming with file.bin
# -U                                - disable write protection
# -P                                - enable write protection
# -A                                - set parameters for 28C16
# -B                                - set parameters for 28C64
# -C                                - set parameters for 28C256
#
# Normally takes 196 seconds to program a 28C64, and 32 seconds to read.
# --
# Chris Baird,, <cjb@brushtail.apana.org.au> threw
# this together during an all-nighter on 2017-Oct-19.
# minor alterations/add. functions by Peter Sieg (peter.sieg1@gmx.de) in 2018:
# -b
# This version: 2018-Jan-02.

import sys
import serial
import time
import argparse

RECSIZE = 16
NL = chr(10)

parser = argparse.ArgumentParser()
parser.add_argument("-V", "--version", help="version", action="store_true")
parser.add_argument("-d", "--debug", help="debug", action="store_true")
parser.add_argument("-p", "--port", help="device, default /dev/ttyUSB0", default='/dev/ttyUSB0')
parser.add_argument("-b", type=int, help="blank eeprom with 0xff")
parser.add_argument("-r", type=int, nargs=2, help="read eeprom to terminal or file")
parser.add_argument("-v", type=argparse.FileType("rb"), help="verify programming with file.bin")
parser.add_argument("-s", type=argparse.FileType("rb"), help="program eeprom with file.bin")
parser.add_argument("-S", type=argparse.FileType("rb"), help="smart programming with file.bin")
parser.add_argument("-U", help="disable write protection", action="store_true")
parser.add_argument("-P", help="enable write protection", action="store_true")
parser.add_argument("-A", help="set parameters for 28C16", action="store_true")
parser.add_argument("-B", help="set parameters for 28C64", action="store_true")
parser.add_argument("-C", help="set parameters for 28C256", action="store_true")
parser.add_argument("-D", help="poll read after write", action="store_true")
parser.add_argument('args', nargs=argparse.REMAINDER)

opts = parser.parse_args()

ser = serial.Serial(opts.port, 9600, timeout=0.1)
time.sleep(1.0)

dumpstart = -1
dumpend = -1
romsize = 2048

def calcwriteline(a, l):
    ck = 0
    s = "W" + ("%04x" % a) + ":"
    for c in l:
        s = s + ("%02x" % ord(c))
        ck = ck ^ ord(c)
    s = s + "ffffffffffffffffffffffffffffffff"
    s = s[:38]
    if (len(l) & 1):
        ck = ck ^ 255
    ck = ck & 255
    s = s + "," + ("%02x" % ck)
    return s.upper()


def cmd(s, w=False):
    if opts.debug:
        print '>', repr(s)
    ser.write(s + NL)
    if w:
        s = waitokay()
    else:
        s = ser.readline()
        if opts.debug:
            print '<', repr(s)
    return s

def waitokay():
    bad = 0
    while True:
        s = ser.readline()
        if opts.debug:
            print '<', repr(s)
        if s == "OK\r\n":
            return s
        else:
            bad = bad + 1
        if bad > 50:
            sys.exit("eh")

def parseRecord(l):
    rom = [None]*RECSIZE
    for p in range(RECSIZE):
        i = 5 + (p*2)
        c = int(l[i:i+2], 16)
        rom[p] = c
    return rom

def recordToText(a, rom):
    romt = "%04x:" % a
    for p in range(RECSIZE):
        romt = romt + str(" %02x" % rom[p])
    return romt

def recordCheksum(rom):
    ck = 0
    for p in range(len(rom)):
        ck = ck ^ rom[p]
    return ck

def binToRecord(r):
    rec = [None]*len(r)
    for i in range(len(r)):
        rec[i] = ord(r[i])
    return rec



if opts.version:
    print cmd('V')
    sys.exit()

#s = sys.argv[0]

if opts.A:
    cmd('A')
if opts.B:
    cmd('B')
if opts.C:
    cmd('C')
if opts.D:
    cmd('D')
if opts.U:
    cmd('U')
if opts.P:
    cmd('P')

if opts.b:
    a = 0
    romsize = int(opts.b)
    while True:
        s = "W" + ("%04x" % a) + ":ffffffffffffffffffffffffffffffff"
        cmd(s, True)
        a = a + RECSIZE
        if a >= romsize:
            break

if opts.r:
    dumpstart = opts.r[0]
    dumpend = opts.r[1]
    if len(opts.args):
        f = open(opts.args[0], 'wb')
    else:
        f = False
    if dumpstart > -1:
        while (dumpstart <= dumpend):
            l = cmd("R%04x" % dumpstart)
            rom = parseRecord(l)
            waitokay()
            if f:
                for p in range(0,len(rom)):
                    f.write(chr(rom[p]))
                f.flush()
                if not opts.debug:
                    print l.upper().strip(), "\r",
                sys.stdout.flush()
            else:
                if not opts.debug:
                    print l.upper().strip()
            ck = recordCheksum(rom)
            val = int(l[38:40],16)
            if (val != ck):
                sys.exit("chksum " + val + "!=" + ck)
            dumpstart = dumpstart + RECSIZE
        if f:
            print

if opts.s:
    f = opts.s
    #f = open(opts.s, 'rb')
    a = 0
    while True:
        l = f.read(RECSIZE)
        if len(l) == 0:
            break
        s = calcwriteline(a, l)
        if opts.debug != True:
            print s, "\r",
            sys.stdout.flush()
        cmd(s, True);
        if len(l) != RECSIZE:
            break
        a = a + RECSIZE
    f.close()
    print

if opts.v:
    f = opts.v
    #f = open(sys.argv[1], 'rb')
    a = 0
    badcount = 0
    while True:
        r = f.read(RECSIZE)
        if len(r) == 0:
            break
        okay = 1
        rec = binToRecord(r)

        l = cmd("R%04x" % a)
        waitokay()
        rom = parseRecord(l)
        print "ROM ", recordToText(a, rom), "\r",
        sys.stdout.flush()

        filet = "FILE %04x:" % a
        for i in range(len(r)):
            if rom[i] != rec[i]:
                okay = 0
                badcount = badcount + 1
                filet = filet + "*%02x" % rec[i]
            else:
                filet = filet + " %02x" % rec[i]

        if okay == 0:
            print
            print filet,
            print "MISMATCH!!"
            #sys.exit()

        if len(r) != RECSIZE:
            break
        else:
            a = a + RECSIZE

    print
    print badcount, "errors!"
    f.close()


if opts.S:
    f = opts.S
    #f = open(sys.argv[1], 'rb')
    a = 0
    while True:
        l = cmd("R%04x" % a)
        waitokay()
        rom = parseRecord(l)
        print "ROM ", recordToText(a, rom),

        r = f.read(RECSIZE)
        if len(r) == 0:
            break
        okay = 1
        filet = "FILE %04x:" % a
        for i in range(len(r)):
            if rom[i] != ord(r[i]):
                okay = 0
                filet = filet + "*%02x" % ord(r[i])
            else:
                filet = filet + " %02x" % ord(r[i])

        if okay == 0:
            s = calcwriteline(a, r)
            print
            print filet, "UPDATING"
            cmd(s, True)
        else:
            print " OKAY"

        if len(r) != RECSIZE:
            break
        else:
            a = a + RECSIZE

    f.close()

###
