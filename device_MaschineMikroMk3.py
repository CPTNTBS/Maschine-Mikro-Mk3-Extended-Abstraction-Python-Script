# name=Maschine Mikro Mk3

import math
import midi
import device
import plugins
import mixer
import ui
import transport

"""
#----------------------------------------OVERRIDES----------------------------------------#
"""

shiftToggle = 0x0

def OnInit():
	shiftToggle = 0x0

def OnMidiMsg(event):
	global shiftToggle

	event.handled = False


	if event.midiId == 0xB0:
		if event.data1 == 0x07:
			focused = {0:0, 1:1, 2:2, 3:3, 4:4}
		elif event.data1 == 0x37:
			CustomTransportMessage(110) # Metronome Toggle
			#if ui.getFocusedFormID() == {}
		elif event.data1 == 0x26:
			shiftToggle = event.data2 # Shift Toggle (Hold)
			print(shiftToggle)
		elif event.data1 == 0x51:
			CustomTransportMessage(64)
		elif event.data1 == 0x52:
			CustomTransportMessage(66)
		elif event.data1 == 0x54:
			CustomTransportMessage(68)
		elif event.data1 == 0x53:
			CustomTransportMessage(65)
		else:
			if shiftToggle == 0x0:
				if event.data1 == 0x28:
					windowToggleAndFocus(4) # Browser Focus
				elif event.data1 == 0x27:
					CustomTransportMessage(67) # Plugin Picker
				else:
					switcher = {
						0x35: transport.setLoopMode, # Pattern / Playlist Loop
						0x39: transport.start, # Play / Pause
						0x3A: transport.record, # Record
						0x3B: transport.stop, # Stop
					}

					func = switcher.get(event.data1, default)

					func()
			else:
				if event.data1 == 0x3A:
					CustomTransportMessage(115) # Countdown
					ui.setHintMsg("Countdown Before Start")
				elif event.data1 == 0x27:
					CustomTransportMessage() # Plugin Picker
					ui.setHintMsg("Plugin Picker")
				elif event.data1 == 0x35:
					CustomTransportMessage(113) # Loop Recording
					ui.setHintMsg("Loop Recording")
				else:
					switcher = {
						0x39: transport.start, # Play / Pause
						0x3B: transport.stop,  # Stop
					}

					func = switcher.get(event.data1, default)

					func()

		



"""
#----------------------------------------HELPER METHODS----------------------------------------#
"""

def default():
	print("Not programmed ... Yet")

def windowToggleAndFocus(window):
	#print (ui.getVisible(window))
	#print (ui.getFocused(window))
	print ()
	print(ui.getFocusedFormCaption())
	if ui.getVisible(window) == 0:
		ui.showWindow(window)
	elif ui.getFocused(window) == 0:
		ui.setFocused(window)
	else:
		ui.hideWindow(window)
		ui.setFocused(window)

def CustomTransportMessage(fPTee):
	transport.globalTransport(fPTee, fPTee, 2, 15)
# Streamlined Midi Messaage sending to Device
#	- command = CC Type (Control Change, Note On, Pitch Bend, etc)
#	- channel = (Apperantly, not so sure) the channel that the device handles output you want
#	- data1 = the individual controller (encoder, button, slider, led, etc) that you want to change (shift by 8).
#	- data2 = the value you want to send. (bit shift by 16).
def SendMIDI(command, channel, data1, data2):
	device.midiOutMsg((command | channel) + (data1 << 8) + (data2 << 16));


# Endless Encoder Fix Status - TO DO
#	- Made for ENC 3FH/41H mode.
#		- When a value of 65 is given, the encoder sends a midi value of
#			newValue = currentValue + 1
#		- When a value of 63 is given, the encoder sends a midi value of
#			newValue = currentValue - 1
def EndlessEncoder(encVal):
	if encVal == 65:
		print('MixVal + 1')
	elif encVal == 63:
		print('MixVal - 1')

# Get method for EventData
def GetEventID(track,slot,param):
	return (((0x2000 + 0x40 * track) + slot) << 0x10) + 0x8000 + param

# Get method for Plugin Track
def GetFocusedPluginTrack():
	return math.floor((ui.getFocusedFormID() >> 16) / 64)

# Get method for Plugin Slot
def GetFocusedPluginSlot():
	return (ui.getFocusedFormID() >> 16) % 64

# Debugging method for checking focused plugins
def GetFocusedWindowInfo():
	trackNumber = GetFocusedPluginTrack()
	slotNumber = GetFocusedPluginSlot()
	print("Current Plugin: " + str(plugins.getPluginName(trackNumber, slotNumber)))
	if trackNumber == 0:
		print("Location: Master Track, Slot " + str(slotNumber + 1))
	else:
		print("Location: Track " + str(trackNumber) + ", Slot " + str(slotNumber + 1))

	print("Linkable Parameters:")
	for param in range(4240): #Every plugin (effects at least) carries 4240 plugins
		while plugins.getParamName(param, trackNumber, slotNumber) != "": #Unnamed Midi CC (ones w/ default MIDI CC#) are just blank strings
			print("     - " + plugins.getParamName(param, trackNumber, slotNumber))
	print("Plugin ID: " + str(hex(ui.getFocusedFormID())))
	print("----------------------------------------------")

# Debugging method for ControlID and EventId of current CC Value
def GetIDS(event):
	print("CC Value: " + str(event.data1))
	print("Control ID: " + str(hex(midi.EncodeRemoteControlID(device.getPortNumber(), event.midiChan, event.data1))))
	print("Event ID: " + str(hex(device.findEventID(midi.EncodeRemoteControlID(device.getPortNumber(), event.midiChan, event.data1)))))

# Debugging method for Channel Data?
def PrintEncoderData(encoder):
	for channelNr in range(0, 4):
		ID = device.findEventID(midi.EncodeRemoteControlID(device.getPortNumber(), channelNr, encoder), 0)
		print(device.getLinkedInfo(ID))
	
"""
#----------------------------------------APPENDIX----------------------------------------#
FUNCTIONALITY IN USE:
	Play Button: Play / Pause Playback
	Record Button: Record
	Stop Button: Stop Playback


GENERAL INFORMATION:
	CONTROL CHANGE MESSAGES
		- 176 = B0 = Base Control Change Byte
		- B0 + Channel = any other channel
	SHIFT ENCODERS:
		- SHIFT CC TYPE = B0 (Base Channel), B4 (Shift Channel)
		- B1 = Default CC Channel that activates secondary channel
	HANDLING MIDI MESSAGES
		- When a MIDI message is not handled, it doesn't control anything in FL/is not told to do anything in FL by the script/There is some task that it needs to do before it can be considered 'handled.'
			- Using it will do the default ish that FL would make it do w/o the script.
			- Ex: Linking parameters to encoders, notes and their values, etc.
		- Only handle parts of the device (channels, CCs, etc) when there is something specific that you want the control to do (change to this color when this happens, send this data back to the device when this happens, etc.).
			- Some Channels and Settings (Channel 3, Reset Encoder Val) don't need to be handled b/c they more or less do things exclusively to the device itself and nothing to the DAW.
	SETTING TWO ANIMATIONS:
		- You can set two animataons via the secondary LED animation channel (2 & 5)
	DEVICE CC VALUES
		- CC Numbers on Device: 0-63 (64 different CCs)
			- Controls With Side button functionality: 0, 1, 2, 3, 8.
	PLUGINID COMPUTATION (EFFECT):
		- Base 10: (track << 6 + slot) << 16
		- Base 16: (track << 0x06 + slot) << 0x10
	EVENTID COMPUTATION:
		- Base 10: (((0x2000 + 0x40 * track) + slot) << 0x10) + 0x8000 + param
		- Base 16: (((8192 + 64 * track) + slot) << 16) + 32768 + param
	CONTROLID COMPUTATION:
		- Base 10: (8388608 + 65536 * channel) + ctrl
		- Base 16: (0x800000 + 0x10000 * channel) + ctrl
	FL TERM GLOSSARY:
		- eventData = input from the device
		- data1 = device cc
		- data2 = device cc amount
		- midiId = midi codes (see midi.py)
		- midiChan = midi channel
		- status = midiId + midiChan
	FL REFRESH FLAGS:
		- 0x20 = DAW Unload Component
		- 0x127 = DAW Load Component, Focus Plugin
		- 0x1000 = Plugin Parameter Change
		- 0x1200 = Linked Control Change
		- 0x4127 = New Plugin

TENTATIVE MIDI FIGHTER TWISTER BANK SETUP:
	BANK 1: Effects
		- Bottom Right: Dry/Wet Mix
	BANK 2: Generator
	BANK 3: Misc. FL
	BANK 4: Free
"""
