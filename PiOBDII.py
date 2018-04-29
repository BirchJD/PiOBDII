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
#/* 2018-04-29 V1.01 - Implemented ELM327 class. Finding all valid PIDs.    */
#/*                    Running all valid PIDs and displaying the results.   */
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


import sys
import pygame
import ELM327
import Display


#  /***************************/
# /* Initialise application. */
#/***************************/
def InitApp():
	# Initialise PyGame environment for graphics and sound.
	pygame.init()
	pygame.mixer.init()
	pygame.font.init()
#	ThisSurface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
	ThisVideoInfo = pygame.display.Info()
	# Hide mouse pointer, using a touch screen for click events.
#	pygame.mouse.set_visible(False)

	return ThisVideoInfo


#  /*********************/
# /* Exit application. */
#/*********************/
def EndApp():
	# Close the ELM327 device after use.
	ThisELM327.Close()
	# Show mouse pointer before ending application.
	pygame.mouse.set_visible(True)
	# Terminate application.
	quit()



#  /***************************************/
# /* Create application class instances. */
#/***************************************/
ThisELM327 = ELM327.ELM327()


# Initialise the application.
ThisVideoInfo = InitApp()

print("DISPLAY: " + str(ThisVideoInfo.current_w) + " x " + str(ThisVideoInfo.current_h))

print("CONNECTING TO CAN BUS FOR OBDII COMMUNICATION...")
if ThisELM327.IsELM327Present() == False:
	print("FAILED TO CONNECT TO ELM327 DEVICE.")
elif ThisELM327.Connect() == False:
	print("FAILED TO CONNECT TO CAN BUS.")
else:
	if ThisELM327.GetInitResult() != "":
		print(ThisELM327.GetInitResult())

	# Display ELM327 information.
	print(ThisELM327.GetInfo())

	# Get a list of all valid PIDs the connected ECU supports.
	ValidPIDs = ThisELM327.GetValidPIDs()
	# Get the information available for each of the supported PIDs.
	for PID in ValidPIDs:
#		if ValidPIDs[PID][0] != '!':
		# Display the information returned for the current PID.
		print("[" + PID + "] " + ValidPIDs[PID] + " : " + str(ThisELM327.DoPID(PID)))

# Exit the application.
EndApp()

