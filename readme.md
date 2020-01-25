# EEprom programmer with Mega 2560

Links:
http://danceswithferrets.org/geekblog/?page_id=903

http://danceswithferrets.org/geekblog/?p=496

Just upload sketch into Mega 2560 arduino.
Build and attach adapter (LED's + resistors are optional):

PCB Eagle+Gerber (Elecrow/Jlcpcb) are in pcb:

![PCB](/img/EEpromer.png)

2 Jumper at 1 are for 28C256 and 28C64.
2 Jumper at 2 are for 28C16.

PCB's arrived and they work as expected.

![JCLPCB](/img/EEprommer%20Adapter.jpeg)

See eeprom.ino and eeprommer.py for details

---
Hardware variant 2 uses Meag 2560 Mini Pro.

Atmega 2560 Pins 31 - 4 are connected to EEPROM
```
 D4---A14 -+---+- VCC---5V
 D6---A12 -+ E +- /WE---D7
 D8----A7 -+ E +- A13---D9
D10----A6 -+ P +- A8----D11
D12----A5 -+ R +- A9 ---D13
D14----A4 -+ O +- A11---D15
D16----A3 -+ M +- /OE---D17
D18----A2 -+   +- A10---D19
D20----A1 -+   +- /CE---D21
D22----A0 -+   +- D7----D23
D24----D0 -+   +- D6----D25
D26----D1 -+   +- D5----D27
D28----D2 -+   +- D4----D29
GND---GND -+---+- D3----D31
```
![img1](/img/IMG_20200125_221945.jpg)
![img1](/img/IMG_20200125_222004.jpg)

