#!/usr/bin/python3

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#/***************************************************************************/
#/* Raspberry Pi ELM327 OBBII CAN BUS Diagnostic Software.                  */
#/*                                                                         */
#/* (C) Jason Birch 2018-04-27 V1.00                                        */
#/*                                                                         */
#/* 2018-04-29 V1.01 - Implemented ELM327 class. Finding all valid PIDs.    */
#/*                    Running all valid PIDs and displaying the results.   */
#/*                                                                         */
#/* 2018-05-01 V1.02 - Added initial graphical user interface components.   */
#/*                                                                         */
#/* 2018-05-09 V1.03 - Icons on buttons, lock meters, additional buttons    */
#/*                    and arrange buttons. Tested bluetooth ELM327 device. */
#/*                                                                         */
#/* Initial OBDII Python application to read trouble codes from the ECU and */
#/* display each trouble code along with it's human readable description.   */
#/*                                                                         */
#/* In this initial version, the user must update the constant at the top   */
#/* of the program code, SERIAL_PORT_NAME, with the serial port which is    */
#/* to be used. Future verstions of the code should have a graphical        */
#/* interface for configuration and provide more features than just reading */
#/* trouble codes.                                                          */
#/***************************************************************************/


import datetime
import _thread
import pygame
import ELM327
import Visual
import Button
import Gadgit
import Select
import Confirm
import Display



DISPLAY_PERIOD = 100
TIMER_PERIOD = 250
READ_ELM_COUNT = 24


# Start value for pygame user events.
EVENT_TIMER = pygame.USEREVENT + 1

# Lock to prevent ELM327 communications occuring when an existing one still running.
LockELM327 = _thread.allocate_lock()

# List of visual class instances to be flashed.
FlashVisuals = {}

#  /***************************************/
# /* Create application class instances. */
#/***************************************/
ThisELM327 = ELM327.ELM327()
ThisDisplay = Display.Display()



#/******************************************************/
#/* Display visual instances in their current Z order. */
#/******************************************************/
def DebugDisplayZOrder():
	Count = 0
	for ThisVisual in Visual.VisualZOrder:
		Count += 1
		print(str(Count) + " " + ThisVisual.GetName() + " " + str(ThisVisual))



#/***************************************************/
#/* Perform a connection to the CAN BUS of the ECU. */
#/***************************************************/
def ConnectELM327(ThisDisplay):
	# Stop flashing MIL light before attempting a new connection.
	FlashVisuals.pop("MIL", None)
	ThisDisplay.Buttons["MIL"].SetDown(False)
	# Flash connect button during connection attempt.
	FlashVisuals["CONNECT"] = ThisDisplay.ELM327Info["CONNECT"]
	try:
		# Notify the user a connection attempt is taking place.
		ThisDisplay.SetVisualText(ThisDisplay.ELM327Info, "INFO", "CONNECTING TO CAN BUS FOR OBDII COMMUNICATION...\n", False)
		# Connect to the CAN BUS of the ECU.
		Result = ThisELM327.Connect()
		# Notify the user of any failures.
		if Result == ELM327.CONNECT_ELM327_FAIL:
			ThisDisplay.SetVisualText(ThisDisplay.ELM327Info, "INFO", "FAILED TO CONNECT TO ELM327 DEVICE.\n", True)
		elif Result == ELM327.CONNECT_CAN_BUS_FAIL:
			ThisDisplay.SetVisualText(ThisDisplay.ELM327Info, "INFO", "FAILED TO CONNECT TO CAN BUS.\n", True)
		else:
			# Display issues initializing the ELM327 device.
			ThisDisplay.SetVisualText(ThisDisplay.ELM327Info, "INFO", ThisELM327.GetInitResult(), False)
			# Display ELM327 information.
			ThisDisplay.SetVisualText(ThisDisplay.ELM327Info, "INFO", "\n" + ThisELM327.GetInfo(), True)
	except Exception as Catch:
		print(str(Catch))
	# Stop flashing connect button after connection attempt.
	FlashVisuals.pop("CONNECT", None)
	ThisDisplay.ELM327Info["CONNECT"].SetDown(False)
	# Check for MIL status after connection attempt.
	if ThisELM327.GetMilOn() == True:
		FlashVisuals["MIL"] = ThisDisplay.Buttons["MIL"]
	# Allow another ELM327 communication now this one is complete.
	LockELM327.release()



#/**********************************************/
#/* Get a frame of all valid PIDs for Mode 01. */
#/**********************************************/
def FrameData(ThisDisplay):
	try:
		# Get a list of all valid PIDs the connected ECU supports.
		ValidPIDs = ThisELM327.GetValidPIDs()
		# Get the information available for each of the supported PIDs.
		ThisDisplay.SetVisualText(ThisDisplay.FrameData, "INFO", "", False)
		for PID in sorted(ValidPIDs):
			if ValidPIDs[PID][0] != '!':
				# Display the information returned for the current PID.
				if PID[1] == '1':
					PidData = ThisELM327.DoPID(PID)
					ThisDisplay.SetVisualText(ThisDisplay.FrameData, "INFO", "[" + PID + "] " + ValidPIDs[PID] + "\n", True, PidData)
	except Exception as Catch:
		print(str(Catch))
	# Allow another ELM327 communication now this one is complete.
	LockELM327.release()



#/**********************************************/
#/* Get a frame of all valid PIDs for Mode 09. */
#/**********************************************/
def VehicleData(ThisDisplay):
	try:
		# Get a list of all valid PIDs the connected ECU supports.
		ValidPIDs = ThisELM327.GetValidPIDs()
		# Get the information available for each of the supported PIDs.
		ThisDisplay.SetVisualText(ThisDisplay.VehicleInfo, "INFO", "", False)
		for PID in sorted(ValidPIDs):
			if ValidPIDs[PID][0] != '!':
				# Display the information returned for the current PID.
				if PID[1] == '9':
					PidData = ThisELM327.DoPID(PID)
					ThisDisplay.SetVisualText(ThisDisplay.VehicleInfo, "INFO", "[" + PID + "] " + ValidPIDs[PID] + "\n", True, PidData)
	except Exception as Catch:
		print(str(Catch))
	# Allow another ELM327 communication now this one is complete.
	LockELM327.release()



#/****************************************/
#/* Get all trouble related information. */
#/****************************************/
def TroubleInfo(ThisDisplay):
	try:
		# Get a list of all valid PIDs the connected ECU supports.
		ValidPIDs = ThisELM327.GetValidPIDs()
		# Display test information and MIL light status.
		PidData = sorted(ThisELM327.DoPID("0101"))
		ThisDisplay.SetVisualText(ThisDisplay.TroubleInfo, "INFO", "[0101] " + ValidPIDs["0101"] + "\n", False, PidData)

		# Display all stored trouble codes and descriptions.
		TroubleCodes = ThisELM327.DoPID("03")
		ThisDisplay.SetVisualText(ThisDisplay.TroubleInfo, "INFO", "\nSTORED TROUBLE CODES: [" + str(len(TroubleCodes)) + "]\n", True)
		if TroubleCodes != ELM327.STRING_ERROR:
			for TroubleCode in sorted(TroubleCodes):
				ThisDisplay.SetVisualText(ThisDisplay.TroubleInfo, "INFO", str(TroubleCode) + " " + str(TroubleCodes[TroubleCode]) + "\n", True)

		# Display all pending trouble codes and descriptions.
		TroubleCodes = ThisELM327.DoPID("07")
		ThisDisplay.SetVisualText(ThisDisplay.TroubleInfo, "INFO", "\nPENDING TROUBLE CODES [" + str(len(TroubleCodes)) + "]:\n", True)
		if TroubleCodes != ELM327.STRING_ERROR:
			for TroubleCode in sorted(TroubleCodes):
				ThisDisplay.SetVisualText(ThisDisplay.TroubleInfo, "INFO", str(TroubleCode) + " " + str(TroubleCodes[TroubleCode]) + "\n", True)
	except Exception as Catch:
		print(str(Catch))
	# Allow another ELM327 communication now this one is complete.
	LockELM327.release()



#/*********************************************/
#/* Clear all trouble codes and related data. */
#/*********************************************/
def ClearTroubleInfo(ThisDisplay):
	try:
		TroubleCodes = ThisELM327.DoPID("04")
	except Exception as Catch:
		print(str(Catch))
	# Allow another ELM327 communication now this one is complete.
	LockELM327.release()
	if LockELM327.acquire(0):
		_thread.start_new_thread(TroubleInfo, (ThisDisplay, ))



#/*********************************************************/
#/* Update the data for the created gadgits from the ECU. */
#/*********************************************************/
def MeterData(ThisDisplay):
	try:
		# Get the information available for each of the meter related PIDs.
		for ThisGadgit in ThisDisplay.Meters:
			if type(ThisDisplay.Meters[ThisGadgit]) is Gadgit.Gadgit:
				PID = ThisDisplay.Meters[ThisGadgit].GetPID()
				if PID != "":
					# Store the information returned for the current PID on the related meter.
					PidData = ThisELM327.DoPID(PID)
					ThisDisplay.Meters[ThisGadgit].SetData(PidData)
	except Exception as Catch:
		print(str(Catch))
	# Allow another ELM327 communication now this one is complete.
	LockELM327.release()




# Create a timer for updating the displayed time/date and updating gadgit data from the ECU.
pygame.time.set_timer(EVENT_TIMER, TIMER_PERIOD)

# Aquire a lock for use when communicating with the ELM327 device.
if LockELM327.acquire(0):
	_thread.start_new_thread(ConnectELM327, (ThisDisplay, ))

# Application message loop.
ExitFlag = False
ReadElmCount = READ_ELM_COUNT
while ExitFlag == False:
	pygame.time.wait(DISPLAY_PERIOD)

	# Process pygame events.
	for ThisEvent in pygame.event.get():
		# If pygame says quit, finish the application.
		if ThisEvent.type == pygame.QUIT:
			ExitFlag = True
		elif ThisEvent.type == pygame.KEYDOWN:
			KeysPressed = pygame.key.get_pressed()
			# If the ESC key is pressed, finish the application.
			if KeysPressed[pygame.K_ESCAPE]:
				ExitFlag = True
		elif ThisEvent.type == EVENT_TIMER:
			# Update the displayed date and time.
			Now = datetime.datetime.now()
			NowTime = Now.strftime("%H:%M")
			NowDate = Now.strftime("%Y-%m-%d")
			ThisDisplay.SetVisualText(ThisDisplay.CurrentTab, "TIME", NowTime)
			ThisDisplay.SetVisualText(ThisDisplay.CurrentTab, "DATE", NowDate)

			# Flash visual instances flagged to be flashed.
			for ThisVisual in FlashVisuals:
				if FlashVisuals[ThisVisual].GetDown() == False:
					FlashVisuals[ThisVisual].SetDown(True)
				else:
					FlashVisuals[ThisVisual].SetDown(False)

			# Unhighlight pressed buttons which are not latch or toggle.
			for ThisButton in ThisDisplay.Buttons:
				if ThisButton not in FlashVisuals and ThisDisplay.Buttons[ThisButton].GetPressType() == Visual.PRESS_DOWN:
					ThisDisplay.Buttons[ThisButton].SetDown(False)
			for ThisGadget in ThisDisplay.CurrentTab:
				if type(ThisDisplay.CurrentTab[ThisGadget]) is Button.Button:
					if ThisGadget not in FlashVisuals and ThisDisplay.CurrentTab[ThisGadget].GetPressType() == Visual.PRESS_DOWN:
						ThisDisplay.CurrentTab[ThisGadget].SetDown(False)
				if type(ThisDisplay.CurrentTab[ThisGadget]) is Gadgit.Gadgit:
					for ThisButton in ThisDisplay.CurrentTab[ThisGadget].Buttons:
						if ThisDisplay.CurrentTab[ThisGadget].Buttons[ThisButton].GetPressType() == Visual.PRESS_DOWN:
							ThisDisplay.CurrentTab[ThisGadget].Buttons[ThisButton].SetDown(False)

			# Update the gadgit data from the ECU.
			ReadElmCount -= 1
			if ThisDisplay.CurrentTab == ThisDisplay.Meters and ReadElmCount <= 0:
				if LockELM327.acquire(0):
					ReadElmCount = READ_ELM_COUNT
					MeterData(ThisDisplay)
		# Only process the following events if the ELM327 device is not currently communicating.
		elif LockELM327.locked() == False:
			if ThisEvent.type == pygame.MOUSEBUTTONDOWN:
				# Pass button down events to all buttons and gadgits.
				ButtonGadgit = ThisDisplay.IsEvent(Visual.EVENT_MOUSE_DOWN, ThisEvent.pos[0], ThisEvent.pos[1], ThisEvent.button)
				print(str(ButtonGadgit))
				if ButtonGadgit != False:
					# If exit button is pressed, finish the application.
					if ButtonGadgit["BUTTON"] == "EXIT":
						# Display a confirmation to exit the application.
						ThisDisplay.CurrentTab["CONFIRM"] = Confirm.Confirm(ThisDisplay.ThisSurface, "CONFIRM_EXIT", "Exit the application?")
					# If confirm dialog button yes is pressed, close the dialog.
					elif ButtonGadgit["BUTTON"] == "YES":
						ThisDisplay.CurrentTab.pop("CONFIRM", None)
						if ButtonGadgit["GADGIT"] == "CONFIRM_EXIT":
							ExitFlag = True
						elif ButtonGadgit["GADGIT"] == "CONFIRM_CLEAR_ECU":
							if LockELM327.acquire(0):
								_thread.start_new_thread(ClearTroubleInfo, (ThisDisplay, ))
					# If confirm dialog button no is pressed, close the dialog.
					elif ButtonGadgit["BUTTON"] == "NO":
						ThisDisplay.CurrentTab.pop("CONFIRM", None)
					# If select dialog selection is made, close the dialog.
					elif "SELECTED" in ButtonGadgit:
						ThisDisplay.CurrentTab.pop("SELECT", None)
						if ButtonGadgit["SELECTED"] != False and ButtonGadgit["GADGIT"] == "SELECT_PID":
							SelectLines = SelectText.split('\n')
							SelectedLine = SelectLines[ButtonGadgit["SELECTED"]]
							ThisPID = SelectedLine[SelectedLine.find("[") + 1:SelectedLine.find("]")]
							# Get a list of all valid PIDs the connected ECU supports.
							ValidPIDs = ThisELM327.GetValidPIDs()
							if ThisPID in ValidPIDs:
								ThisDisplay.Meters[SelectGadgit].SetPID(ThisPID, ValidPIDs[ThisPID])
					# If print button is pressed.
					elif ButtonGadgit["BUTTON"] == "PRINT":
						# Display NOT IMPLEMENTED YET.
						ThisDisplay.CurrentTab["CONFIRM"] = Confirm.Confirm(ThisDisplay.ThisSurface, "CONFIRM_TBA", "THIS FEATURE\nNOT IMPLEMENTED CURRENTLY")
					# If save button is pressed.
					elif ButtonGadgit["BUTTON"] == "SAVE":
						# Display NOT IMPLEMENTED YET.
						ThisDisplay.CurrentTab["CONFIRM"] = Confirm.Confirm(ThisDisplay.ThisSurface, "CONFIRM_TBA", "THIS FEATURE\nNOT IMPLEMENTED CURRENTLY")
					# If configure button is pressed.
					elif ButtonGadgit["BUTTON"] == "CONFIG":
						# Display NOT IMPLEMENTED YET.
						ThisDisplay.CurrentTab["CONFIRM"] = Confirm.Confirm(ThisDisplay.ThisSurface, "CONFIRM_TBA", "THIS FEATURE\nNOT IMPLEMENTED CURRENTLY")
					# If connect button is pressed, connect to the CAN BUS.
					elif ButtonGadgit["BUTTON"] == "CONNECT":
						if LockELM327.acquire(0):
							_thread.start_new_thread(ConnectELM327, (ThisDisplay, ))
					# If select button is pressed, select a PID for the specific gadgit.
					elif ButtonGadgit["BUTTON"] == "SELECT":
						# Remember which gadgit the select is for.
						SelectGadgit = ButtonGadgit["GADGIT"]
						# Get a list of all valid PIDs the connected ECU supports.
						ValidPIDs = ThisELM327.GetValidPIDs()
						# Get the information available for each of the supported PIDs.
						SelectText = ""
						for PID in sorted(ValidPIDs):
							if ValidPIDs[PID][0] != '!':
								PidDescription = ValidPIDs[PID].split("|")
								SelectText += "[" + PID + "] " + PidDescription[0] + "\n"
						# Display a PID selection dialog.
						ThisDisplay.CurrentTab["SELECT"] = Select.Select(ThisDisplay.ThisSurface, "SELECT_PID", SelectText)
					# If vehicle button is pressed, get the vehicle data from the ECU.
					elif ButtonGadgit["BUTTON"] == "CLOSE":
						ThisDisplay.CurrentTab.pop("SELECT", None)
					elif ButtonGadgit["BUTTON"] == "VEHICLE":
						if LockELM327.acquire(0):
							_thread.start_new_thread(VehicleData, (ThisDisplay, ))
					# If trouble or refresh button is pressed, get the trobule related data from the ECU.
					elif ButtonGadgit["BUTTON"] == "TROUBLE" or ButtonGadgit["BUTTON"] == "MIL" or ButtonGadgit["BUTTON"] == "REFRESH":
						if LockELM327.acquire(0):
							_thread.start_new_thread(TroubleInfo, (ThisDisplay, ))
							# Check for MIL status after reading trouble data.
							FlashVisuals.pop("MIL", None)
							ThisDisplay.Buttons["MIL"].SetDown(False)
							if ThisELM327.GetMilOn() == True:
								FlashVisuals["MIL"] = ThisDisplay.Buttons["MIL"]
					# If clear button is pressed, clear the trouble and related data on the ECU.
					elif ButtonGadgit["BUTTON"] == "CLEAR":
						# Display a confirmation to clear ECU trouble codes.
						ThisDisplay.CurrentTab["CONFIRM"] = Confirm.Confirm(ThisDisplay.ThisSurface, "CONFIRM_CLEAR_ECU", "Clear all trouble codes\nand related data\non the ECU?")
					# If plots button is pressed.
					elif ButtonGadgit["BUTTON"] == "PLOTS":
						# Display NOT IMPLEMENTED YET.
						ThisDisplay.CurrentTab["CONFIRM"] = Confirm.Confirm(ThisDisplay.ThisSurface, "CONFIRM_TBA", "THIS FEATURE\nNOT IMPLEMENTED CURRENTLY")
					# If freeze button is pressed.
					elif ButtonGadgit["BUTTON"] == "FREEZE" or ButtonGadgit["BUTTON"] == "RELOAD_FREEZE":
						# Display NOT IMPLEMENTED YET.
						ThisDisplay.CurrentTab["CONFIRM"] = Confirm.Confirm(ThisDisplay.ThisSurface, "CONFIRM_TBA", "THIS FEATURE\nNOT IMPLEMENTED CURRENTLY")
					# If frame button is pressed, get a frame of data from the ECU.
					elif ButtonGadgit["BUTTON"] == "FRAME" or ButtonGadgit["BUTTON"] == "RELOAD":
						if LockELM327.acquire(0):
							_thread.start_new_thread(FrameData, (ThisDisplay, ))
			elif ThisEvent.type == pygame.MOUSEBUTTONUP:
				# Pass button up events to all buttons and gadgits.
				ButtonGadgit = ThisDisplay.IsEvent(Visual.EVENT_MOUSE_UP, ThisEvent.pos[0], ThisEvent.pos[1], ThisEvent.button)
			elif ThisEvent.type == pygame.MOUSEMOTION:
				# When a button is down, pass movement events to all buttons and gadgits.
				if ThisEvent.buttons[0] > 0:
					ButtonGadgit = ThisDisplay.IsEvent(Visual.EVENT_MOUSE_MOVE, ThisEvent.pos[0], ThisEvent.pos[1], ThisEvent.buttons[0])
				else:
					ButtonGadgit = ThisDisplay.IsEvent(Visual.EVENT_MOUSE_HOVER, ThisEvent.pos[0], ThisEvent.pos[1], ThisEvent.buttons[0])

	# Update the display.
	ThisDisplay.Display()


# Terminate application.
pygame.time.set_timer(EVENT_TIMER, 0)
ThisDisplay.Close()
quit()

