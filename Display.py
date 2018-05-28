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
#/* (C) Jason Birch 2018-05-28 V1.08                                        */
#/*                                                                         */
#/* Class: Display                                                          */
#/* Look after a hierarchy of objects to be displayed.                      */
#/***************************************************************************/



import os
import pygame
import Visual
import Button
import Gadgit
import Plot



DEBUG = "OFF"



class Display:
	# List of meters to be displayed on the Meters tab.
	Meters = {}
	Meters["NAME"] = "METERS"

	# List of frame data to be displayed on the frame data tab.
	FrameData = {}
	FrameData["NAME"] = "FRAME_DATA"

	# List of freeze frame data to be displayed on the freeze frame data tab.
	FreezeFrameData = {}
	FreezeFrameData["NAME"] = "FREEZE_FRAME_DATA"

	# List of plots to be displayed on the plots tab.
	Plots = {}
	Plots["NAME"] = "PLOTS"

	# List of trouble code info to be displayed on the vehicle info tab.
	TroubleInfo = {}
	TroubleInfo["NAME"] = "TROUBLE_INFO"

	# List of vehicle info to be displayed on the vehicle info tab.
	VehicleInfo = {}
	VehicleInfo["NAME"] = "VEHICLE_INFO"

	# List of ELM327 info to be displayed on the ELM327 info tab.
	ELM327Info = {}
	ELM327Info["NAME"] = "ELM327_INFO"



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
		if DEBUG == "ON":
			print("DISPLAY: " + str(self.DisplayXLen) + " x " + str(self.DisplayYLen))

		self.SurfaceXLen = pygame.display.Info().current_w
		self.SurfaceYLen = pygame.display.Info().current_h

		# Scale gagit sizes to a preportion of the display surface.
		self.GadgitWidth = int(self.SurfaceXLen / 3)
		self.GadgitHeight = int((self.SurfaceYLen - Visual.BUTTON_HEIGHT) / 1.4)
		self.ButtonWidth = int(self.SurfaceXLen / 12)

		# Define the buttons to be displayed on the background.
		self.Buttons = {
			"METERS" : Button.Button(self.ThisSurface, "METERS", Visual.PRESS_LATCH, 2*self.ButtonWidth, 0, self.ButtonWidth, Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Meters.png"),
			"FRAME" : Button.Button(self.ThisSurface, "FRAME", Visual.PRESS_LATCH, 3*self.ButtonWidth, 0, self.ButtonWidth, Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Frame.png"),
			"FREEZE" : Button.Button(self.ThisSurface, "FREEZE", Visual.PRESS_LATCH, 4*self.ButtonWidth, 0, self.ButtonWidth, Visual.BUTTON_HEIGHT, "IMAGE:ICONS/FreezeFrame.png"),
			"PLOTS" : Button.Button(self.ThisSurface, "PLOTS", Visual.PRESS_LATCH, 5*self.ButtonWidth, 0, self.ButtonWidth, Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Plots.png"),
			"TROUBLE" : Button.Button(self.ThisSurface, "TROUBLE", Visual.PRESS_LATCH, 6*self.ButtonWidth, 0, self.ButtonWidth, Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Trouble.png"),
			"VEHICLE" : Button.Button(self.ThisSurface, "VEHICLE", Visual.PRESS_LATCH, 7*self.ButtonWidth, 0, self.ButtonWidth, Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Vehicle.png"),
			"ELM327" : Button.Button(self.ThisSurface, "ELM327", Visual.PRESS_LATCH, 8*self.ButtonWidth, 0, self.ButtonWidth, Visual.BUTTON_HEIGHT, "IMAGE:ICONS/OBDII.png"),
			"BUSY" : Button.Button(self.ThisSurface, "BUSY", Visual.PRESS_DOWN, self.DisplayXLen-2*self.ButtonWidth, 0, self.ButtonWidth, Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Busy.png"),
			"EXIT" : Button.Button(self.ThisSurface, "EXIT", Visual.PRESS_DOWN, self.DisplayXLen-self.ButtonWidth, 0, self.ButtonWidth, Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Exit.png"),

			"MIL" : Button.Button(self.ThisSurface, "MIL", Visual.PRESS_DOWN, 0, Visual.BUTTON_HEIGHT, self.ButtonWidth, Visual.BUTTON_HEIGHT, "IMAGE:ICONS/MIL_Off.png", DownText = "IMAGE:ICONS/MIL_On.png"),
			"SAVE" : Button.Button(self.ThisSurface, "SAVE", Visual.PRESS_DOWN, self.ButtonWidth, Visual.BUTTON_HEIGHT, self.ButtonWidth, Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Save.png"),
			"PRINT" : Button.Button(self.ThisSurface, "PRINT", Visual.PRESS_DOWN, 2*self.ButtonWidth, Visual.BUTTON_HEIGHT, self.ButtonWidth, Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Print.png"),
			"DATE" : Button.Button(self.ThisSurface, "DATE", Visual.PRESS_NONE, 4*self.ButtonWidth, Visual.BUTTON_HEIGHT, 2*self.ButtonWidth, Visual.BUTTON_HEIGHT, "DATE"),
			"TIME" : Button.Button(self.ThisSurface, "TIME", Visual.PRESS_NONE, 6*self.ButtonWidth, Visual.BUTTON_HEIGHT, 2*self.ButtonWidth, Visual.BUTTON_HEIGHT, "TIME"),
		}

		# Define the meters tab area for the display.
		self.Meters["LOCK"] = Button.Button(self.ThisSurface, "LOCK", Visual.PRESS_TOGGLE, 0, 0, self.ButtonWidth, Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Lock_Off.png", DownText = "IMAGE:ICONS/Lock_On.png")
		self.Meters["ADD"] = Button.Button(self.ThisSurface, "ADD", Visual.PRESS_DOWN, self.ButtonWidth, 0, self.ButtonWidth, Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Add.png")
		self.Meters["GO_STOP"] = Button.Button(self.ThisSurface, "GO_STOP", Visual.PRESS_TOGGLE, self.DisplayXLen-3*self.ButtonWidth, 0, self.ButtonWidth, Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Go.png", DownText = "IMAGE:ICONS/Stop.png")

		# Define the frame data tab area for the display.
		self.FrameData["INFO"] = Button.Button(self.ThisSurface, "INFO", Visual.PRESS_NONE, 0, 2*Visual.BUTTON_HEIGHT, self.DisplayXLen, self.DisplayYLen - 2*Visual.BUTTON_HEIGHT, "", Visual.ALIGN_TEXT_LEFT)
		self.FrameData["RELOAD"] = Button.Button(self.ThisSurface, "RELOAD", Visual.PRESS_DOWN, self.DisplayXLen - self.ButtonWidth, Visual.BUTTON_HEIGHT, self.ButtonWidth, Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Reload.png")

		# Define the freeze frame data tab area for the display.
		self.FreezeFrameData["INFO"] = Button.Button(self.ThisSurface, "INFO", Visual.PRESS_NONE, 0, 2*Visual.BUTTON_HEIGHT, self.DisplayXLen, self.DisplayYLen - 2*Visual.BUTTON_HEIGHT, "", Visual.ALIGN_TEXT_LEFT)
		self.FreezeFrameData["RELOAD_FREEZE"] = Button.Button(self.ThisSurface, "RELOAD_FREEZE", Visual.PRESS_DOWN, self.DisplayXLen - self.ButtonWidth, Visual.BUTTON_HEIGHT, self.ButtonWidth, Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Reload.png")

		# Define the plot tab area for the display.
		self.Plots["PLOT"] = Plot.Plot(self.ThisSurface, "PLOT", Visual.PRESS_NONE, 0, 2*Visual.BUTTON_HEIGHT, self.DisplayXLen, self.DisplayYLen - 2*Visual.BUTTON_HEIGHT, "")
		self.Plots["GO_STOP"] = Button.Button(self.ThisSurface, "GO_STOP", Visual.PRESS_TOGGLE, self.DisplayXLen-3*self.ButtonWidth, 0, self.ButtonWidth, Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Go.png", DownText = "IMAGE:ICONS/Stop.png")
		self.Plots["PLOT_1"] = Button.Button(self.ThisSurface, "PLOT_1", Visual.PRESS_DOWN, self.DisplayXLen - 4*self.ButtonWidth, Visual.BUTTON_HEIGHT, self.ButtonWidth, Visual.BUTTON_HEIGHT, "[1]")
		self.Plots["PLOT_2"] = Button.Button(self.ThisSurface, "PLOT_2", Visual.PRESS_DOWN, self.DisplayXLen - 3*self.ButtonWidth, Visual.BUTTON_HEIGHT, self.ButtonWidth, Visual.BUTTON_HEIGHT, "[2]")
		self.Plots["PLOT_3"] = Button.Button(self.ThisSurface, "PLOT_3", Visual.PRESS_DOWN, self.DisplayXLen - 2*self.ButtonWidth, Visual.BUTTON_HEIGHT, self.ButtonWidth, Visual.BUTTON_HEIGHT, "[3]")
		self.Plots["RESET"] = Button.Button(self.ThisSurface, "RESET", Visual.PRESS_DOWN, self.DisplayXLen - self.ButtonWidth, Visual.BUTTON_HEIGHT, self.ButtonWidth, Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Reset.png")

		# Define the trouble tab area for the display.
		self.TroubleInfo["INFO"] = Button.Button(self.ThisSurface, "INFO", Visual.PRESS_NONE, 0, 2*Visual.BUTTON_HEIGHT, self.DisplayXLen, self.DisplayYLen - 2*Visual.BUTTON_HEIGHT, "", Visual.ALIGN_TEXT_LEFT)
		self.TroubleInfo["REFRESH"] = Button.Button(self.ThisSurface, "REFRESH", Visual.PRESS_DOWN, 9*self.ButtonWidth, Visual.BUTTON_HEIGHT, self.ButtonWidth, Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Refresh.png")
		self.TroubleInfo["CLEAR"] = Button.Button(self.ThisSurface, "CLEAR", Visual.PRESS_DOWN, self.DisplayXLen - self.ButtonWidth, Visual.BUTTON_HEIGHT, self.ButtonWidth, Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Clear.png")

		# Define the vehicle tab area for the display.
		self.VehicleInfo["INFO"] = Button.Button(self.ThisSurface, "INFO", Visual.PRESS_NONE, 0, 2*Visual.BUTTON_HEIGHT, self.DisplayXLen, self.DisplayYLen - 2*Visual.BUTTON_HEIGHT, "", Visual.ALIGN_TEXT_LEFT)

		# Define the ELM327 tab area for the display.
		self.ELM327Info["INFO"] = Button.Button(self.ThisSurface, "INFO", Visual.PRESS_NONE, 0, 2*Visual.BUTTON_HEIGHT, self.DisplayXLen, self.DisplayYLen - 2*Visual.BUTTON_HEIGHT, "", Visual.ALIGN_TEXT_LEFT)
		self.ELM327Info["CONFIG"] = Button.Button(self.ThisSurface, "CONFIG", Visual.PRESS_DOWN, 9*self.ButtonWidth, Visual.BUTTON_HEIGHT, self.ButtonWidth, Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Config.png")
		self.ELM327Info["CONNECT"] = Button.Button(self.ThisSurface, "CONNECT", Visual.PRESS_DOWN, self.DisplayXLen - self.ButtonWidth, Visual.BUTTON_HEIGHT, self.ButtonWidth, Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Connect.png")

		# Currently selected tab, default meters.
		self.CurrentTab = self.ELM327Info
		self.Buttons["ELM327"].SetDown(True)
		self.Buttons["BUSY"].SetVisible(False)



#/****************************************************/
#/* Perform required tasks when closing the display. */
#/****************************************************/
	def Close(self):
		# Show mouse pointer before ending application.
		pygame.mouse.set_visible(True)



#/************************************/
#/* Return the width of the display. */
#/************************************/
	def GetDisplayWidth(self):
		return self.DisplayXLen



#/*************************************/
#/* Return the height of the display. */
#/*************************************/
	def GetDisplayHeight(self):
		return self.DisplayYLen



#/*******************************************/
#/* Load gadgits onto meters tab from disk. */
#/*******************************************/
	def LoadMetersTab(self, ValidPIDs):
		try:
			if os.path.isfile("CONFIG/METERS.CFG"):
				File = open("CONFIG/METERS.CFG", 'r')
				xPos = 0
				Name = ""
				TextLine = "."
				while TextLine != "":
					TextLine = File.readline()
					TextLine = TextLine.replace("\n", "")
					TextElements = TextLine.split('|')
					for ThisElement in TextElements:
						if ThisElement[:5] == "Name=":
							Name = str(ThisElement[5:])
							self.Meters[Name] = Gadgit.Gadgit(self.ThisSurface, Name, Visual.PRESS_NONE, 0, 2 * Visual.BUTTON_HEIGHT, self.GadgitWidth, self.GadgitHeight, "NEW")
						elif ThisElement[:5] == "xPos=":
							xPos = float(ThisElement[5:])
						elif ThisElement[:5] == "yPos=":
							self.Meters[Name].SetPos(xPos, float(ThisElement[5:]))
						elif ThisElement[:6] == "Style=":
							self.Meters[Name].SetStyle(float(ThisElement[6:]))
						elif ThisElement[:4] == "PID=":
							ThisPID = str(ThisElement[4:])
							ThisPidDescription = ""
							if ThisPID in ValidPIDs:
								ThisPidDescription = ValidPIDs[ThisPID]
							self.Meters[Name].SetPID(ThisPID, ThisPidDescription)
				File.close()

				# Hide buttons on meteres, default locked.
				self.Meters["LOCK"].SetDown(True)
				self.Meters["ADD"].SetVisible(False)
				for ThisGadget in self.Meters:
					if type(self.Meters[ThisGadget]) is not str and type(self.Meters[ThisGadget]) is not Button.Button:
						for ThisButton in self.Meters[ThisGadget].Buttons:
							self.Meters[ThisGadget].Buttons[ThisButton].SetVisible(False)
		except:
			# On fail remove all loaded gadgets.
			for ThisGadget in self.Meters:
				if type(self.Meters[ThisGadget]) is not str and type(self.Meters[ThisGadget]) is not Button.Button:
					self.Meters.pop([ThisGadget], None)



#/*****************************************/
#/* Save gadgits from meters tab to disk. */
#/*****************************************/
	def SaveMetersTab(self):
		if len(self.Meters) > 1:
			File = open("CONFIG/METERS.CFG", 'w')
			for ThisGadget in self.Meters:
				if type(self.Meters[ThisGadget]) is not str and type(self.Meters[ThisGadget]) is not Button.Button:
					Data = "Name=" + str(self.Meters[ThisGadget].GetName())
					Data += "|xPos=" + str(self.Meters[ThisGadget].GetXPos())
					Data += "|yPos=" + str(self.Meters[ThisGadget].GetYPos())
					Data += "|Style=" + str(self.Meters[ThisGadget].GetStyle())
					Data += "|PID=" + str(self.Meters[ThisGadget].GetPID())
					File.write(Data + "\n")
			File.close()



#/***********************************************************/
#/* Check if an event occurred on the display. Perform any  */
#/* required actions and let the caller know if the display */
#/* area was touched.                                       */
#/***********************************************************/
	def IsEvent(self, EventType, xPos, yPos, PointerButton, xOffset = 0, yOffset = 0):
		Result = False

		# Check for gadgit touches on the currently selected tab only, in the correct Z order.
		for ThisVisual in reversed(Visual.VisualZOrder):
			for ThisGadget in self.CurrentTab:
				if type(self.CurrentTab[ThisGadget]) is not str and self.CurrentTab[ThisGadget] == ThisVisual:
					Result = self.CurrentTab[ThisGadget].IsEvent(EventType, xPos, yPos, PointerButton, xOffset, yOffset)
					if Result != False:
						if EventType == Visual.EVENT_MOUSE_DOWN:
							# When a gadgit is clicked, bring it to the front of other gadgits.
							TopGagitIndex = len(Visual.VisualZOrder) - 1
							ThisGadgitIndex = Visual.VisualZOrder.index(self.CurrentTab[ThisGadget])
							Visual.VisualZOrder[TopGagitIndex] = Visual.VisualZOrder[ThisGadgitIndex]
							for MoveGadgitIndex in range(ThisGadgitIndex, TopGagitIndex):
								Visual.VisualZOrder[MoveGadgitIndex] = Visual.VisualZOrder[MoveGadgitIndex + 1]
							# If a gadgit close button was pressed, remove the gadgit.
							if DEBUG == "ON":
								print(str(Result))
							if Result["BUTTON"] == "CLOSE":
								self.CurrentTab.pop(ThisGadget, None)
						break
			if Result != False:
				break

		# If no gadgits were touched, check for button touches.
		if Result == False:
			for ThisButton in self.Buttons:
				Result = self.Buttons[ThisButton].IsEvent(EventType, xPos, yPos, PointerButton, xOffset, yOffset)
				if Result != False:
					if EventType == Visual.EVENT_MOUSE_DOWN:
						# Switch tabs when a tab button is pressed.
						if Result["BUTTON"] == "METERS":
							self.CurrentTab = self.Meters
						elif Result["BUTTON"] == "FRAME":
							self.CurrentTab = self.FrameData
						elif Result["BUTTON"] == "FREEZE":
							self.CurrentTab = self.FreezeFrameData
						elif Result["BUTTON"] == "PLOTS":
							self.CurrentTab = self.Plots
						elif Result["BUTTON"] == "TROUBLE" or Result["BUTTON"] == "MIL":
							self.CurrentTab = self.TroubleInfo
						elif Result["BUTTON"] == "VEHICLE":
							self.CurrentTab = self.VehicleInfo
						elif Result["BUTTON"] == "ELM327":
							self.CurrentTab = self.ELM327Info
					break

			# If a button was touched, highlight only the current tab.
			if Result != False:
				if self.CurrentTab != self.Meters:
					self.Buttons["METERS"].SetDown(False)
				if self.CurrentTab != self.FrameData:
					self.Buttons["FRAME"].SetDown(False)
				if self.CurrentTab != self.FreezeFrameData:
					self.Buttons["FREEZE"].SetDown(False)
				if self.CurrentTab != self.Plots:
					self.Buttons["PLOTS"].SetDown(False)
				if self.CurrentTab != self.TroubleInfo:
					self.Buttons["TROUBLE"].SetDown(False)
				if self.CurrentTab != self.VehicleInfo:
					self.Buttons["VEHICLE"].SetDown(False)
				if self.CurrentTab != self.ELM327Info:
					self.Buttons["ELM327"].SetDown(False)

		return Result



#/***********************************************/
#/* Set the text on the gadgit or button of the */
#/* specified name on the specified tab.        */
#/***********************************************/
	def SetVisualText(self, Tab, VisualName, NewText, Append = False, DataValue = 0):
		for ThisGadget in Tab:
			if type(Tab[ThisGadget]) is not str:
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

		# Display all gadgets on the selected tab in the correct Z order.
		for ThisVisual in Visual.VisualZOrder:
			for ThisGadget in self.CurrentTab:
				if type(self.CurrentTab[ThisGadget]) is not str and self.CurrentTab[ThisGadget] == ThisVisual:
					self.CurrentTab[ThisGadget].Display(self.ThisSurface)

		# Update the display.
		pygame.display.flip()

