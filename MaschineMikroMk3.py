#-------------------------------------CLASSES
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs', 'hidapi'))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), 'libs', 'python-rtmidi'))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), 'libs', 'pywin32'))

import hid
import rtmidi
from multiprocessing import Process, Event

#-------------------------------------CLASSES

class ButtonStatus:
	ON = 0x7C
	SELECTED = 0x7E
	OFFDEFAULT = 0x7D
	OFFFULL = 0x00

# Color class used for both the Pads & Strip
class Color:
	OFF = 0x00
	RED = 0x04
	ORANGE = 0x08
	LIGHTORANGE = 0x0C
	WARMYELLOW = 0x10
	YELLOW = 0x14
	LIME = 0x18
	GREEN = 0x1C
	MINT = 0x20
	CYAN = 0x24
	TURQUOISE = 0x28
	BLUE = 0x2C
	PLUM = 0x30
	VIOLET = 0x34
	PURPLE = 0x38
	MAGENTA = 0x3C
	FUCHSIA = 0x40
	WHITE = 0x7C

class MaschineMikroMk3:
      VID = 6092
      PID = 5888

# HID Message Building Blocks
startingByte = [[0x80]] * 1
buttonBytes = [[ButtonStatus.OFFFULL]] * 39
padBytes = [[Color.OFF]] * 16
touchStripBytes = [[Color.OFF]] * 25

# Full HID Message (unflattened)
subHIDMessage = [startingByte, buttonBytes, padBytes, touchStripBytes]

# Convert hidmessage to a list of ints
def flatten_and_convert(hidmessage):
	return [byte for sublist in hidmessage for item in sublist for byte in item]

def setByte(byte, index, hidMessageComponent):
	if isinstance(index, int):
		if index < len(hidMessageComponent[0]):
			hidMessageComponent[0][index] = byte
	elif isinstance(index, list):
		if len(index) == len(hidMessageComponent[0]):
			hidMessageComponent[0][:] = [byte] * len(hidMessageComponent[0])
		else:
			for x in index:			
				if x < len(hidMessageComponent[0]):
					hidMessageComponent[0][x] = byte

def getByte(byte, index, hidMessageComponent):
	if index < len(hidMessageComponent[0]):
		return hidMessageComponent[0][index]


maschine = hid.device()

maschine.open(MaschineMikroMk3.VID, MaschineMikroMk3.PID)
maschine.set_nonblocking(1)
#maschine.write()

hidmessage = flatten_and_convert(subHIDMessage)

print(len(hidmessage))

maschine.write(hidmessage)

#------------------------------------------- MIDI Ish
midiOut = rtmidi.MidiOut()
midiIn = rtmidi.MidiIn()

print("Available MIDI input ports:")
for port_num in range(midiIn.get_port_count()):
    print(f"[{port_num}] {midiIn.get_port_name(port_num)}")

# In python-rtmidi (at least), the only way to get a specific port number is by name.
def getPortNumber(deviceName=None):
    midiIn = rtmidi.MidiIn()
    portNumber = None
    
    try:
        for i in range(midiIn.get_port_count()):
            portName = midiIn.get_port_name(i)
            if portName == f"{deviceName} {i}":
                portNumber = i
                break
    finally:
        del midiIn

    if portNumber is None:
        print(f"Port for {deviceName} Not Found!")
    
    return portNumber

# callback function to concurrently run
def midiCallback(message, timestamp):
	maschine.write(hidmessage)
	print(f"Received MIDI message: {message}")


portNumber = getPortNumber("Maschine Mikro MK3")

if portNumber is not None:
	midiIn.open_port(portNumber)
midiOut.open_virtual_port("MIDISCRIPT")

midiIn.set_callback(midiCallback)

try:
    input("Press Enter to stop...\n")
except KeyboardInterrupt:
    pass
finally:
    midiIn.close_port()
    del midiIn