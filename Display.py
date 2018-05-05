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
#/* (C) Jason Birch 2018-05-01 V1.02                                        */
#/*                                                                         */
#/* Class: Display                                                          */
#/* Look after a hierarchy of objects to be displayed.                      */
#/***************************************************************************/


import pygame
import Visual
import Button
import Gadgit
import Plot


class Display:
	BUTTON_HEIGHT = 50


	# List of meters to be displayed on the Meters tab.
	Meters = {}

	# List of frame data to be displayed on the frame data tab.
	FrameData = {}

	# List of freeze frame data to be displayed on the freeze frame data tab.
	FreezeFrameData = {}

	# List of plots to be displayed on the plots tab.
	Plots = {}

	# List of trouble code info to be displayed on the vehicle info tab.
	TroubleInfo = {}

	# List of vehicle info to be displayed on the vehicle info tab.
	VehicleInfo = {}

	# List of ELM327 info to be displayed on the ELM327 info tab.
	ELM327Info = {}

	# Currently selected tab, default meters.
	CurrentTab = ELM327Info



	def __init__(self):
		# Initialise PyGame environment for graphics and sound.
		pygame.init()
		pygame.mixer.init()
		pygame.font.init()
		self.ThisSurface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
		# Hide mouse pointer, using a touch screen for click events.
#		pygame.mouse.set_visible(False)

		# Get the dimensions of the surface to draw the visual object onto.
		(self.DisplayXLen, self.DisplayYLen) = pygame.Surface.get_size(self.ThisSurface)

		self.SurfaceXLen = pygame.display.Info().current_w
		self.SurfaceYLen = pygame.display.Info().current_h

		# Scale gagit sizes to a preportion of the display surface.
		self.GadgitWidth = int(self.SurfaceXLen / 4)
		self.GadgitHeight = int((self.SurfaceYLen - self.BUTTON_HEIGHT) / 2)
		self.ButtonWidth = int(self.SurfaceXLen / 20)

		# Define the buttons to be displayed on the background.
		self.Buttons = {
			"LOCK" : Button.Button(self.ThisSurface, "LOCK", 0, 0, self.ButtonWidth, self.BUTTON_HEIGHT, "LOCK"),
			"ADD" : Button.Button(self.ThisSurface, "ADD", self.ButtonWidth, 0, self.ButtonWidth, self.BUTTON_HEIGHT, "ADD"),
			"MIL" : Button.Button(self.ThisSurface, "MIL", 2*self.ButtonWidth, 0, self.ButtonWidth, self.BUTTON_HEIGHT, "MIL"),

			"METERS" : Button.Button(self.ThisSurface, "METERS", 3*self.ButtonWidth, 0, 2*self.ButtonWidth, self.BUTTON_HEIGHT, "METERS"),
			"FRAME" : Button.Button(self.ThisSurface, "FRAME", 5*self.ButtonWidth, 0, 2*self.ButtonWidth, self.BUTTON_HEIGHT, "FRAME"),
			"FREEZE" : Button.Button(self.ThisSurface, "FREEZE", 7*self.ButtonWidth, 0, 2*self.ButtonWidth, self.BUTTON_HEIGHT, "FREEZE"),
			"PLOTS" : Button.Button(self.ThisSurface, "PLOTS", 9*self.ButtonWidth, 0, 2*self.ButtonWidth, self.BUTTON_HEIGHT, "PLOTS"),
			"TROUBLE" : Button.Button(self.ThisSurface, "TROUBLE", 11*self.ButtonWidth, 0, 2*self.ButtonWidth, self.BUTTON_HEIGHT, "TROUBLE"),
			"VEHICLE" : Button.Button(self.ThisSurface, "VEHICLE", 13*self.ButtonWidth, 0, 2*self.ButtonWidth, self.BUTTON_HEIGHT, "VEHICLE"),
			"ELM327" : Button.Button(self.ThisSurface, "ELM327", 15*self.ButtonWidth, 0, 2*self.ButtonWidth, self.BUTTON_HEIGHT, "ELM327"),

			"DATE" : Button.Button(self.ThisSurface, "DATE", 17*self.ButtonWidth, 0, 2*self.ButtonWidth, self.BUTTON_HEIGHT/2, "DATE"),
			"TIME" : Button.Button(self.ThisSurface, "TIME", 17*self.ButtonWidth, 25, 2*self.ButtonWidth, self.BUTTON_HEIGHT/2, "TIME"),
			"EXIT" : Button.Button(self.ThisSurface, "EXIT", self.DisplayXLen-self.ButtonWidth, 0, self.ButtonWidth, self.BUTTON_HEIGHT, "EXIT"),
		}

		# Define the tab areas for the display.
		self.FrameData["INFO"] = Button.Button(self.ThisSurface, "INFO", 0, 2*self.BUTTON_HEIGHT, self.DisplayXLen, self.DisplayYLen - 2*self.BUTTON_HEIGHT, "", Visual.Visual.ALIGN_TEXT_LEFT)
		self.FrameData["RELOAD"] = Button.Button(self.ThisSurface, "RELOAD", 0, self.BUTTON_HEIGHT, 2*self.ButtonWidth, self.BUTTON_HEIGHT, "RELOAD")

		self.Plots["PLOT"] = Plot.Plot(self.ThisSurface, "PLOT", 0, 2*self.BUTTON_HEIGHT, self.DisplayXLen, self.DisplayYLen - self.BUTTON_HEIGHT, "")
		self.Plots["RESET"] = Button.Button(self.ThisSurface, "RESET", self.DisplayXLen - 2*self.ButtonWidth, self.BUTTON_HEIGHT, 2*self.ButtonWidth, self.BUTTON_HEIGHT, "RESET")

		self.TroubleInfo["REFRESH"] = Button.Button(self.ThisSurface, "REFRESH", 0, self.BUTTON_HEIGHT, 2*self.ButtonWidth, self.BUTTON_HEIGHT, "REFRESH")
		self.TroubleInfo["CLEAR"] = Button.Button(self.ThisSurface, "CLEAR", self.DisplayXLen - 2*self.ButtonWidth, self.BUTTON_HEIGHT, 2*self.ButtonWidth, self.BUTTON_HEIGHT, "CLEAR")

		self.TroubleInfo["INFO"] = Button.Button(self.ThisSurface, "INFO", 0, 2*self.BUTTON_HEIGHT, self.DisplayXLen, self.DisplayYLen - 2*self.BUTTON_HEIGHT, "", Visual.Visual.ALIGN_TEXT_LEFT)

		self.VehicleInfo["INFO"] = Button.Button(self.ThisSurface, "INFO", 0, 2*self.BUTTON_HEIGHT, self.DisplayXLen, self.DisplayYLen - 2*self.BUTTON_HEIGHT, "", Visual.Visual.ALIGN_TEXT_LEFT)

		self.ELM327Info["INFO"] = Button.Button(self.ThisSurface, "INFO", 0, 2*self.BUTTON_HEIGHT, self.DisplayXLen, self.DisplayYLen - 2*self.BUTTON_HEIGHT, "", Visual.Visual.ALIGN_TEXT_LEFT)
		self.ELM327Info["CONFIG"] = Button.Button(self.ThisSurface, "CONFIG", 0, self.BUTTON_HEIGHT, 2*self.ButtonWidth, self.BUTTON_HEIGHT, "CONFIG")
		self.ELM327Info["CONNECT"] = Button.Button(self.ThisSurface, "CONNECT", self.DisplayXLen - 2*self.ButtonWidth, self.BUTTON_HEIGHT, 2*self.ButtonWidth, self.BUTTON_HEIGHT, "CONNECT")



#/****************************************************/
#/* Perform required tasks when closing the display. */
#/****************************************************/
	def Close(self):
		# Show mouse pointer before ending application.
		pygame.mouse.set_visible(True)



#/***********************************************************/
#/* Check if an event occurred on the display. Perform any  */
#/* required actions and let the caller know if the display */
#/* area was touched.                                       */
#/***********************************************************/
	def IsEvent(self, EventType, xPos, yPos, PointerButton, xOffset = 0, yOffset = 0):
		self.Result = False

		# Check for button presses.
		for ThisButton in self.Buttons:
			self.Result = self.Buttons[ThisButton].IsEvent(EventType, xPos, yPos, PointerButton, xOffset, yOffset)
			if self.Result != False:
				# Switch tabs when a tab button is pressed.
				if EventType == Visual.Visual.EVENT_MOUSE_DOWN:
					if self.Result["BUTTON"] == "METERS":
						self.CurrentTab = self.Meters
					elif self.Result["BUTTON"] == "FRAME":
						self.CurrentTab = self.FrameData
					elif self.Result["BUTTON"] == "FREEZE":
						self.CurrentTab = self.FreezeFrameData
					elif self.Result["BUTTON"] == "PLOTS":
						self.CurrentTab = self.Plots
					elif self.Result["BUTTON"] == "TROUBLE":
						self.CurrentTab = self.TroubleInfo
					elif self.Result["BUTTON"] == "VEHICLE":
						self.CurrentTab = self.VehicleInfo
					elif self.Result["BUTTON"] == "ELM327":
						self.CurrentTab = self.ELM327Info
				break

		# If no buttons were touched, check for gadgit touches on the currently selected tab only.
		if self.Result == False:
			for ThisGadget in self.CurrentTab:
				self.Result = self.CurrentTab[ThisGadget].IsEvent(EventType, xPos, yPos, PointerButton, xOffset, yOffset)
				if self.Result != False:
					if EventType == Visual.Visual.EVENT_MOUSE_DOWN:
						# If a gadgit close button was pressed, remove the gadgit.
						if self.Result["BUTTON"] == "CLOSE":
							self.CurrentTab.pop(ThisGadget, None)
					break

		return self.Result



#/***********************************************/
#/* Set the text on the gadgit or button of the */
#/* specified name on the specified tab.        */
#/***********************************************/
	def SetVisualText(self, Tab, VisualName, NewText, Append = False, DataValue = 0):
		for ThisGadget in Tab:
			Tab[ThisGadget].Display(self.ThisSurface)
			if Tab[ThisGadget].GetName() == VisualName:
				Tab[ThisGadget].SetText(NewText, Append, DataValue)

		for ThisButton in self.Buttons:
			if self.Buttons[ThisButton].GetName() == VisualName:
				self.Buttons[ThisButton].SetText(NewText, Append, DataValue)



#/*****************************************************/
#/* Draw buttons and gadgits on the provided surface. */
#/*****************************************************/
	def Display(self):
		# Erase the surface.
		self.ThisSurface.fill((0x00, 0x00, 0x00))

		# Display all buttons on the background.
		for ThisButton in self.Buttons:
			self.Buttons[ThisButton].Display(self.ThisSurface)

		# Display all gadgets on the selected tab.
		for ThisGadget in self.CurrentTab:
			self.CurrentTab[ThisGadget].Display(self.ThisSurface)

		# Update the display.
		pygame.display.flip()

