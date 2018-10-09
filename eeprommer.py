#!/usr/bin/env python2.7
# Uses the Arduino firmware given on http://danceswithferrets.org/geekblog/?p=496
#
# -b size (in decimal)              - blank eeprom with 0xff
# -r start end (in decimal)         - read eeprom to terminal
# -s file.bin (programming)         - program eeprom with file.bin
# -v file.bin (verify content)      - verify eeprom with file.bin
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

RECSIZE = 16

#ser = serial.Serial('/dev/ttyACM0', 9600, timeout=0.1)
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.1)
sys.argv.pop(0)
dumpstart = -1
dumpend = -1
romsize = 2048
s = sys.argv[0]


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


def waitokay():
    bad = 0
    while True:
        s = ser.readline()
        if s == "OK\r\n":
            break
        else:
            bad = bad + 1
        if bad > 50:
            sys.exit("eh")


if s == "-A":
    s = "A"
    print s
    ser.write(s + chr(10))
    s = ser.readline()
    print s

if s == "-B":
    s = "B"
    print s
    ser.write(s + chr(10))
    s = ser.readline()
    print s

if s == "-C":
    s = "C"
    print s
    ser.write(s + chr(10))
    s = ser.readline()
    print s

if s == "-U":
    s = "U"
    print s
    ser.write(s + chr(10))
    s = ser.readline()
    print s

if s == "-P":
    s = "P"
    print s
    ser.write(s + chr(10))
    s = ser.readline()
    print s

if s == "-b":
    a = 0
    romsize = int(sys.argv[1])
    while True:
        s = "W" + ("%04x" % a) + ":ffffffffffffffffffffffffffffffff"
        print s
        ser.write(s + chr(10))
        waitokay()
        a = a + RECSIZE
        if a >= romsize:
            break

if s == "-r":
    dumpstart = int(sys.argv[1])
    dumpend = int(sys.argv[2])
    if dumpstart > -1:
        while (dumpstart <= dumpend):
            addr = "%04x" % dumpstart
            s = "R" + addr + chr(10)
            ser.write(s)
            l = ser.readline()
            print l.upper(),
            waitokay()
            dumpstart = dumpstart + RECSIZE


if s == "-s":
    f = open(sys.argv[1], 'rb')
    a = 0
    while True:
        l = f.read(RECSIZE)
        if len(l) == 0:
            break
        s = calcwriteline(a, l)
        print s
        ser.write(s + chr(10))
        waitokay()
        if len(l) != RECSIZE:
            break
        a = a + RECSIZE
    f.close()


if s == "-v":
    f = open(sys.argv[1], 'rb')
    a = 0
    badcount = 0
    while True:
        s = "R" + ("%04x" % a) + chr(10)
        ser.write(s)
        l = ser.readline()
        l = l.upper()
        waitokay()

        romt = "ROM  %04x:" % a

        rom = [None]*RECSIZE
        for p in range(RECSIZE):
            i = 5 + (p*2)
            c = int(l[i:i+2], 16)
            romt = romt + str(" %02x" % c)
            rom[p] = c
        print romt, "\r",
        sys.stdout.flush()

        r = f.read(RECSIZE)
        if len(r) == 0:
            break
        okay = 1
        filet = "FILE %04x:" % a
        for i in range(len(r)):
            filet = filet + " %02x" % ord(r[i])
            if rom[i] != ord(r[i]):
                okay = 0
                badcount = badcount + 1

        if okay == 0:
            print
            print filet
            print "MISMATCH!!"
            print

        if len(r) != RECSIZE:
            break
        else:
            a = a + RECSIZE

    print
    print badcount, "errors!"
    f.close()


if s == "-S":
    f = open(sys.argv[1], 'rb')
    a = 0
    while True:
        s = "R" + ("%04x" % a) + chr(10)
        ser.write(s)
        l = ser.readline()
        l = l.upper()
        waitokay()

        romt = "ROM  %04x:" % a
        rom = [None]*RECSIZE
        for p in range(RECSIZE):
            i = 5 + (p*2)
            c = int(l[i:i+2], 16)
            romt = romt + str(" %02x" % c)
            rom[p] = c
        print romt,

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
            ser.write(s+chr(10))
            waitokay()
        else:
            print " OKAY"

        if len(r) != RECSIZE:
            break
        else:
            a = a + RECSIZE

    f.close()

###
