import sys
import os

#libs_path = os.path.join(os.path.dirname(__file__), 'libs')
#sys.path.append(libs_path)
#sys.path = []
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs', 'hidapi'))
#sys.path.append(r'C:\Users\PALACE\Documents\Image-Line\FL Studio\Settings\Hardware\Maschine Mikro Mk3\libs')
import hid

VID = 6092
PID = 5888

class Button:
	ON = 0x7C
	SELECTED = 0x7E
	OFFDEFAULT = 0x7D
	OFFFULL = 0x00

#Color Class used for Pads/Strips
class Color:
	OFF = 0x00
	WHITE = 0x7C
	WHITESELECTED = 0x7E


#print(hid.enumerate(VID, PID))

maschine = hid.device()

maschine.open(VID, PID)
maschine.set_nonblocking(1)
#maschine.write()

startingByte = [0x80] * 1
buttonBytes = [Button.OFFFULL] * 39
padBytes = [Color.OFF] * 16
touchStripBytes = [Color.OFF] * 25
hidmessage = startingByte + buttonBytes + padBytes + touchStripBytes

print(len(hidmessage))

maschine.write(hidmessage)