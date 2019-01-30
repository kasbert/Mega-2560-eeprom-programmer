# EEprom programmer with Mega 2560

Links:
http://danceswithferrets.org/geekblog/?page_id=903

http://danceswithferrets.org/geekblog/?p=496

Just upload sketch into Mega 2560 arduino.
Build and attach adapter (LED's + resistors are optional):

PCB Eagle+Gerber (Elecrow/Jlcpcb) are in EEpromer.zip:

![PCB](https://github.com/petersieg/eeprom/blob/master/EEpromer.png)

2 Jumper at 1 are for 28C256 and 28C64.
2 Jumper at 2 are for 28C16.

PCB's arrived and they work as expected.

![JCLPCB](https://github.com/petersieg/eeprom/blob/master/EEprommer%20Adapter.jpeg)

Header from INO:

```code
// EEPROM Programmer - code for an Arduino Mega 2560
//
// Written by K Adcock.
//       Jan 2016 - Initial release
//       Dec 2017 - Slide code tartups, to remove compiler errors for new Arduino IDE (1.8.5).
//   7th Dec 2017 - Updates from Dave Curran of Tynemouth Software, adding commands to enable/disable SDP.
//  10th Dec 2017 - Fixed one-byte EEPROM corruption (always byte 0) when unprotecting an EEPROM
//                  (doesn't matter if you write a ROM immediately after, but does matter if you use -unprotect in isolation)
//                - refactored code a bit (split loop() into different functions)
//                - properly looked at timings on the Atmel datasheet, and worked out that my delays
//                  during reads and writes were about 10,000 times too big!
//                  Reading and writing is now orders-of-magnitude quicker.
//  21st Feb 2018 - P. Sieg
//                  static const long int k_uTime_WriteDelay_uS = 500; // delay between byte writes - needed for at28c16
//                  delayMicroseconds(k_uTime_WritePulse_uS);
//  06th Oct 2018 - P. Sieg
//                - corrected SDP (un)protect adresses & k_uTime_WriteDelay_uS
//                - Set parameters -A=28C16; -B=28C64; -C=28C256
//  29th Jan 2019 - P. Sieg
//                - Introduced + and - to alter k_uTime_WritePulse_uS
//
```
---

Python programming script (still a lot of issues - Linux: Need minicom to connect first and leave without reset; OSX: doesn't work at all - always get 'eh'):
```code
#!/usr/bin/env python2.7
# Uses the Arduino firmware given on http://danceswithferrets.org/geekblog/?p=496
#
# -r start end (in decimal)
# -s file.bin (programming)
# -v file.bin (verify content)
# -S file.bin ('smart' programming)
#
# Normally takes 196 seconds to program a 28C64, and 32 seconds to read.
# --
# Chris Baird,, <cjb@brushtail.apana.org.au> threw
# this together during an all-nighter on 2017-Oct-19.
# This version: 2017-Oct-25.
```
