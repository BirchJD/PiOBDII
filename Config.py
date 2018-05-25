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
#/* (C) Jason Birch 2018-05-25 V1.06                                        */
#/*                                                                         */
#/* Class: Config                                                           */
#/* Display a dialog showing a list of configurable items for the           */
#/* application and allow the user to set the values.                       */
#/***************************************************************************/



import os
import pygame
import Visual
import Button



# Configuration default values.
ConfigValues = {
	"FontName" : "freemono",
	"SerialPort" : "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A800eaG9-if00-port0",
	"Vehicle" : "DATA/TroubleCodes-R53_Cooper_S.txt",
	"Debug": "OFF",
}



#/*********************************/
#/* Load configuration from disk. */
#/*********************************/
def LoadConfig():
	if os.path.isfile("CONFIG/CONFIG.CFG"):
		File = open("CONFIG/CONFIG.CFG", 'r')
		TextLine = "."
		while TextLine != "":
			TextLine = File.readline()
			TextLine = TextLine.replace("\n", "")
			if TextLine[:9] == "FontName=":
				ConfigValues["FontName"] = str(TextLine[9:])
			elif TextLine[:11] == "SerialPort=":
				ConfigValues["SerialPort"] = str(TextLine[11:])
			elif TextLine[:8] == "Vehicle=":
				ConfigValues["Vehicle"] = str(TextLine[8:])
			elif TextLine[:6] == "Debug=":
				ConfigValues["Debug"] = str(TextLine[6:])
		File.close()



#/*******************************/
#/* Save configuration to disk. */
#/*******************************/
def SaveConfig():
	File = open("CONFIG/CONFIG.CFG", 'w')
	File.write("FontName=" + str(ConfigValues["FontName"]) + "\n")
	File.write("SerialPort=" + str(ConfigValues["SerialPort"]) + "\n")
	File.write("Vehicle=" + str(ConfigValues["Vehicle"]) + "\n")
	File.write("Debug=" + str(ConfigValues["Debug"]) + "\n")
	File.close()



class Config(Visual.Visual):
	def __init__(self, ThisSurface, Name, Text):
		# Config covers full display surface to prevent other interface items being clicked before the configuration has been saved.
		Visual.Visual.__init__(self, ThisSurface, Name, Visual.PRESS_NONE, 0, 0, Button.Visual.BUTTON_HEIGHT, Button.Visual.BUTTON_HEIGHT, Text)

		# Config covers full display, but only draw in middle so some interface can still be seen, but not used.
		self.xLen = self.DisplayXLen / 1.25
		self.yLen = self.DisplayYLen / 1.25
		self.xPos = (self.DisplayXLen - self.xLen) / 2
		self.yPos = (self.DisplayYLen - self.yLen) / 2
		self.Align = Visual.ALIGN_TEXT_TOP
		self.ColourFill = self.ColourConfigDialog

		# Buttons displayed on the confirm dialog.
		self.Buttons = {
			# Config covers full display with this button to prevent other user interface being used while dialog visible.
			"UI_BLOCKER" : Button.Button(self.ThisSurface, "UI_BLOCKER", Visual.PRESS_NONE, -self.xLen, -self.yLen, self.DisplayXLen, self.DisplayYLen, "UI_BLOCKER"),
			"SELECT_FONT" : Button.Button(self.ThisSurface, "SELECT_FONT", Visual.PRESS_DOWN, Visual.X_MARGIN, 10, Button.Visual.BUTTON_HEIGHT, Button.Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Select.png"),
			"SELECT_SERIAL_PORT" : Button.Button(self.ThisSurface, "SELECT_SERIAL_PORT", Visual.PRESS_DOWN, Visual.X_MARGIN, 85, Button.Visual.BUTTON_HEIGHT, Button.Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Select.png"),
			"SELECT_VEHICLE" : Button.Button(self.ThisSurface, "SELECT_VEHICLE", Visual.PRESS_DOWN, Visual.X_MARGIN, 160, Button.Visual.BUTTON_HEIGHT, Button.Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Select.png"),
			"SELECT_DEBUG" : Button.Button(self.ThisSurface, "SELECT_DEBUG", Visual.PRESS_DOWN, Visual.X_MARGIN, 235, Button.Visual.BUTTON_HEIGHT, Button.Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Select.png"),
			"SAVE_CONFIG" : Button.Button(self.ThisSurface, "SAVE_CONFIG", Visual.PRESS_DOWN, Button.Visual.BUTTON_HEIGHT, self.yLen - 1.5*Button.Visual.BUTTON_HEIGHT, Button.Visual.BUTTON_HEIGHT, Button.Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Config.png"),
			"CLOSE" : Button.Button(self.ThisSurface, "CLOSE", Visual.PRESS_DOWN, self.xLen - 2*Button.Visual.BUTTON_HEIGHT, self.yLen - 1.5*Button.Visual.BUTTON_HEIGHT, Button.Visual.BUTTON_HEIGHT, Button.Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Close.png"),
		}

		self.Buttons["UI_BLOCKER"].SetVisible(False)

		LoadConfig()



#/*****************************************/
#/* Get a list of appropreate font names. */
#/*****************************************/
	def GetFontNameList(self):
		FontNames = ""

		# Find a fixed width fonts, so text can be tabulated.
		for ThisFontName in pygame.freetype.get_fonts():
			if ThisFontName.find("mono") > -1:
				FontNames += ThisFontName + "\n"

		return FontNames



#/************************************************/
#/* Get a list of appropreate serial port names. */
#/************************************************/
	def GetSerialPortNameList(self):
		SerialPortNames = ""

		# Find BlueTooth serial port names.
		try:
			for SerialPortName in os.listdir("/dev/"):
				if SerialPortName[:6] == "rfcomm":
					SerialPortNames += "/dev/" + SerialPortName + "\n"
		except:
			print("Failed to read: /dev/")
		# Find serial port names.
		try:
			for SerialPortName in os.listdir("/dev/serial/by-id/"):
				SerialPortNames += "/dev/serial/by-id/" + SerialPortName + "\n"
		except:
			print("Failed to read: /dev/serial/by-id/")

		return SerialPortNames



#/************************************************/
#/* Get a list of appropreate serial port names. */
#/************************************************/
	def GetVehicleNameList(self):
		VehicleNames = ""

		# Find vehicle names.
		try:
			for VehicleName in os.listdir("./DATA/"):
				if VehicleName[:13] == "TroubleCodes-":
					VehicleNames += "DATA/" + VehicleName + "\n"
		except:
			print("Failed to read: ./")

		return VehicleNames



#/************************************************************************/
#/* Check if an event occurred in this dialog area. Perform any required */
#/* actions and let the caller know if the dialog was touched.           */
#/************************************************************************/
	def IsEvent(self, EventType, xPos, yPos, PointerButton, xOffset = 0, yOffset = 0):
		Result = Visual.Visual.IsEvent(self, EventType, xPos, yPos, PointerButton, xOffset, yOffset)

		# Handle dialog events.
		if Result != False:
			# Tell caller the name of the gague that was touched.
			Result["GADGIT"] = self.Name
			# Tell caller the name of the button on the gague that was touched.
			Result["BUTTON"] = ""
			for ThisButton in self.Buttons:
				ButtonResult = self.Buttons[ThisButton].IsEvent(EventType, xPos, yPos, PointerButton, self.xPos, self.yPos)
				if ButtonResult != False and self.Buttons[ThisButton].GetName() != "UI_BLOCKER":
					Result["BUTTON"] = ThisButton
					break
			if EventType == Visual.EVENT_MOUSE_DOWN:
				if Result["BUTTON"] == "SAVE_CONFIG":
					SaveConfig()
				elif Result["BUTTON"] == "SELECT_DEBUG":
					if ConfigValues["Debug"] == "OFF":
						ConfigValues["Debug"] = "ON"
					else:
						ConfigValues["Debug"] = "OFF"
		else:
			# Always return true, no other user interface is available until this dialog answered.
			Result = {}
			Result["GADGIT"] = self.Name
			Result["BUTTON"] = ""

		return Result



#/*********************************************/
#/* Draw this dialog on the provided surface. */
#/*********************************************/
	def Display(self, ThisSurface, xOffset = 0, yOffset = 0):
		# Display dialog background and border.
		pygame.draw.rect(ThisSurface, self.ColourFill, (xOffset + self.xPos, yOffset + self.yPos, self.xLen, self.yLen), 0)
		pygame.draw.rect(ThisSurface, self.ColourBorder, (xOffset + self.xPos, yOffset + self.yPos, self.xLen, self.yLen), 4)

		# Display the font configuration option.
		ThisText = "Font:"
		TextHeight = Visual.Fonts["LargeFont"].get_rect(ThisText)[3]
		RenderText = Visual.Fonts["LargeFont"].render(ThisText, self.ColourText)
		ThisSurface.blit(RenderText[0], (self.xPos + xOffset + 2*Visual.X_MARGIN + Visual.BUTTON_HEIGHT, self.yPos + yOffset + 10))
		ThisText = ConfigValues["FontName"]
		TextHeight = Visual.Fonts["LargeFont"].get_rect(ThisText)[3]
		RenderText = Visual.Fonts["LargeFont"].render(ThisText, self.ColourValueText)
		ThisSurface.blit(RenderText[0], (self.xPos + xOffset + 2*Visual.X_MARGIN + Visual.BUTTON_HEIGHT, self.yPos + yOffset + 10 + TextHeight + Visual.Y_MARGIN))

		# Display the serial port configuration option.
		ThisText = "Serial Port:"
		TextHeight = Visual.Fonts["LargeFont"].get_rect(ThisText)[3]
		RenderText = Visual.Fonts["LargeFont"].render(ThisText, self.ColourText)
		ThisSurface.blit(RenderText[0], (self.xPos + xOffset + 2*Visual.X_MARGIN + Visual.BUTTON_HEIGHT, self.yPos + yOffset + 85))
		ThisText = ConfigValues["SerialPort"]
		TextHeight = Visual.Fonts["LargeFont"].get_rect(ThisText)[3]
		RenderText = Visual.Fonts["LargeFont"].render(ThisText, self.ColourValueText)
		ThisSurface.blit(RenderText[0], (self.xPos + xOffset + 2*Visual.X_MARGIN + Visual.BUTTON_HEIGHT, self.yPos + yOffset + 85 + TextHeight + Visual.Y_MARGIN))

		# Display the vehicle configuration option.
		ThisText = "Vehicle:"
		TextHeight = Visual.Fonts["LargeFont"].get_rect(ThisText)[3]
		RenderText = Visual.Fonts["LargeFont"].render(ThisText, self.ColourText)
		ThisSurface.blit(RenderText[0], (self.xPos + xOffset + 2*Visual.X_MARGIN + Visual.BUTTON_HEIGHT, self.yPos + yOffset + 160))
		ThisText = ConfigValues["Vehicle"]
		TextHeight = Visual.Fonts["LargeFont"].get_rect(ThisText)[3]
		RenderText = Visual.Fonts["LargeFont"].render(ThisText, self.ColourValueText)
		ThisSurface.blit(RenderText[0], (self.xPos + xOffset + 2*Visual.X_MARGIN + Visual.BUTTON_HEIGHT, self.yPos + yOffset + 160 + TextHeight + Visual.Y_MARGIN))

		# Display the debug configuration option.
		ThisText = "Debug:"
		TextHeight = Visual.Fonts["LargeFont"].get_rect(ThisText)[3]
		RenderText = Visual.Fonts["LargeFont"].render(ThisText, self.ColourText)
		ThisSurface.blit(RenderText[0], (self.xPos + xOffset + 2*Visual.X_MARGIN + Visual.BUTTON_HEIGHT, self.yPos + yOffset + 235))
		ThisText = ConfigValues["Debug"]
		TextHeight = Visual.Fonts["LargeFont"].get_rect(ThisText)[3]
		RenderText = Visual.Fonts["LargeFont"].render(ThisText, self.ColourValueText)
		ThisSurface.blit(RenderText[0], (self.xPos + xOffset + 2*Visual.X_MARGIN + Visual.BUTTON_HEIGHT, self.yPos + yOffset + 235 + TextHeight + Visual.Y_MARGIN))

		# Display all buttons on the gadgit.
		for ThisButton in self.Buttons:
			self.Buttons[ThisButton].Display(self.ThisSurface, self.xPos, self.yPos)

		# Draw any super class elements.
		Visual.Visual.Display(self, ThisSurface, xOffset, yOffset)

