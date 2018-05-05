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
import Gadgit
import Display



# Start value for pygame user events.
EVENT_TIMER = pygame.USEREVENT + 1

# Lock to prevent ELM327 communications occuring when an existing one still running.
LockELM327 = _thread.allocate_lock()

#  /***************************************/
# /* Create application class instances. */
#/***************************************/
ThisELM327 = ELM327.ELM327()
ThisDisplay = Display.Display()



#/***************************************************/
#/* Perform a connection to the CAN BUS of the ECU. */
#/***************************************************/
def ConnectELM327(ThisDisplay):
	try:
		# Notify the user a connection attempt is taking place.
		ThisDisplay.SetVisualText(ThisDisplay.ELM327Info, "INFO", "CONNECTING TO CAN BUS FOR OBDII COMMUNICATION...\n", False)
		# Connect to the CAN BUS of the ECU.
		Result = ThisELM327.Connect()
		# Notify the user of any failures.
		if Result == ThisELM327.CONNECT_ELM327_FAIL:
			ThisDisplay.SetVisualText(ThisDisplay.ELM327Info, "INFO", "FAILED TO CONNECT TO ELM327 DEVICE.\n", True)
		elif Result == ThisELM327.CONNECT_CAN_BUS_FAIL:
			ThisDisplay.SetVisualText(ThisDisplay.ELM327Info, "INFO", "FAILED TO CONNECT TO CAN BUS.\n", True)
		else:
			# Display issues initializing the ELM327 device.
			ThisDisplay.SetVisualText(ThisDisplay.ELM327Info, "INFO", ThisELM327.GetInitResult(), False)
			# Display ELM327 information.
			ThisDisplay.SetVisualText(ThisDisplay.ELM327Info, "INFO", "\n" + ThisELM327.GetInfo(), True)
	except Exception as Catch:
		print(str(Catch))
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
		for PID in ValidPIDs:
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
		for PID in ValidPIDs:
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
		PidData = ThisELM327.DoPID("0101")
		ThisDisplay.SetVisualText(ThisDisplay.TroubleInfo, "INFO", "[0101] " + ValidPIDs["0101"] + "\n", False, PidData)

		# Display all stored trouble codes and descriptions.
		ThisDisplay.SetVisualText(ThisDisplay.TroubleInfo, "INFO", "\nSTORED TROUBLE CODES:\n", True)
		TroubleCodes = ThisELM327.DoPID("03")
		if TroubleCodes != ThisELM327.STRING_ERROR:
			for TroubleCode in TroubleCodes:
				ThisDisplay.SetVisualText(ThisDisplay.TroubleInfo, "INFO", str(TroubleCode) + " " + str(TroubleCodes[TroubleCode]) + "\n", True)

		# Display all pending trouble codes and descriptions.
		ThisDisplay.SetVisualText(ThisDisplay.TroubleInfo, "INFO", "\nPENDING TROUBLE CODES:\n", True)
		TroubleCodes = ThisELM327.DoPID("07")
		if TroubleCodes != ThisELM327.STRING_ERROR:
			for TroubleCode in TroubleCodes:
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
			PID = ThisDisplay.Meters[ThisGadgit].GetPID()
			if PID != "":
				# Store the information returned for the current PID on the related meter.
				PidData = ThisELM327.DoPID(PID)
				ThisDisplay.Meters[ThisGadgit].SetData(PidData)
	except Exception as Catch:
		print(str(Catch))
	# Allow another ELM327 communication now this one is complete.
	LockELM327.release()




# Aquire a lock for use when communicating with the ELM327 device.
if LockELM327.acquire(0):
	_thread.start_new_thread(ConnectELM327, (ThisDisplay, ))

# Create a timer for updating the displayed time/date and updating gadgit data from the ECU.
pygame.time.set_timer(EVENT_TIMER, 2000)

# Application message loop.
ExitFlag = False
while ExitFlag == False:
	pygame.time.wait(100)

	# Process pygame events.
	for ThisEvent in pygame.event.get():
		if ThisEvent.type == EVENT_TIMER:
			# Update the displayed date and time.
			Now = datetime.datetime.now()
			NowTime = Now.strftime("%H:%M")
			NowDate = Now.strftime("%Y-%m-%d")
			ThisDisplay.SetVisualText(ThisDisplay.CurrentTab, "TIME", NowTime)
			ThisDisplay.SetVisualText(ThisDisplay.CurrentTab, "DATE", NowDate)

			# Update the gadgit data from the ECU.
			if ThisDisplay.CurrentTab == ThisDisplay.Meters:
				if LockELM327.acquire(0):
					MeterData(ThisDisplay)
		# Only process the following events if the ELM327 device is not currently communicating.
		elif LockELM327.locked() == False:
			# If pygame says quit, finish the application.
			if ThisEvent.type == pygame.QUIT:
				ExitFlag = True
			elif ThisEvent.type == pygame.KEYDOWN:
				KeysPressed = pygame.key.get_pressed()
				# If the ESC key is pressed, finish the application.
				if KeysPressed[pygame.K_ESCAPE]:
					ExitFlag = True
			elif ThisEvent.type == pygame.MOUSEBUTTONDOWN:
				# Pass button down events to all buttons and gadgits.
				ButtonGadgit = ThisDisplay.IsEvent(Visual.Visual.EVENT_MOUSE_DOWN, ThisEvent.pos[0], ThisEvent.pos[1], ThisEvent.button)
				print(str(ButtonGadgit))
				if ButtonGadgit != False:
					# If exit button is pressed, finish the application.
					if ButtonGadgit["BUTTON"] == "EXIT":
						ExitFlag = True
					# If add button is pressed, add a new gadgit to the meters tab.
					elif ButtonGadgit["BUTTON"] == "ADD":
						ThisDisplay.Meters["NEW"] = Gadgit.Gadgit(ThisDisplay.ThisSurface, "NEW", 0, ThisDisplay.BUTTON_HEIGHT, ThisDisplay.GadgitWidth, ThisDisplay.GadgitHeight, "NEW")
						ThisPID = "0105"
						# Get a list of all valid PIDs the connected ECU supports.
						ValidPIDs = ThisELM327.GetValidPIDs()
						if ThisPID in ValidPIDs:
							ThisDisplay.Meters["NEW"].SetPID(ThisPID, ValidPIDs[ThisPID])
					# If connect button is pressed, connect to the CAN BUS.
					elif ButtonGadgit["BUTTON"] == "CONNECT":
						if LockELM327.acquire(0):
							_thread.start_new_thread(ConnectELM327, (ThisDisplay, ))
					# If vehicle button is pressed, get the vehicle data from the ECU.
					elif ButtonGadgit["BUTTON"] == "VEHICLE":
						if LockELM327.acquire(0):
							_thread.start_new_thread(VehicleData, (ThisDisplay, ))
					# If trouble or refresh button is pressed, get the trobule related data from the ECU.
					elif ButtonGadgit["BUTTON"] == "TROUBLE" or ButtonGadgit["BUTTON"] == "REFRESH":
						if LockELM327.acquire(0):
							_thread.start_new_thread(TroubleInfo, (ThisDisplay, ))
					# If clear button is pressed, clear the trouble and related data on the ECU.
					elif ButtonGadgit["BUTTON"] == "CLEAR":
						if LockELM327.acquire(0):
							_thread.start_new_thread(ClearTroubleInfo, (ThisDisplay, ))
					# If frame button is pressed, get a frame of data from the ECU.
					elif ButtonGadgit["BUTTON"] == "FRAME" or ButtonGadgit["BUTTON"] == "RELOAD":
						if LockELM327.acquire(0):
							_thread.start_new_thread(FrameData, (ThisDisplay, ))
			elif ThisEvent.type == pygame.MOUSEBUTTONUP:
				# Pass button up events to all buttons and gadgits.
				ButtonGadgit = ThisDisplay.IsEvent(Visual.Visual.EVENT_MOUSE_UP, ThisEvent.pos[0], ThisEvent.pos[1], ThisEvent.button)
			elif ThisEvent.type == pygame.MOUSEMOTION:
				# When a button is down, pass movement events to all buttons and gadgits.
				if ThisEvent.buttons[0] > 0:
					ButtonGadgit = ThisDisplay.IsEvent(Visual.Visual.EVENT_MOUSE_MOVE, ThisEvent.pos[0], ThisEvent.pos[1], ThisEvent.buttons[0])

	# Update the display.
	ThisDisplay.Display()


# Terminate application.
pygame.time.set_timer(EVENT_TIMER, 0)
ThisDisplay.Close()
quit()

