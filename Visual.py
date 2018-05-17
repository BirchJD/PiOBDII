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
#/* (C) Jason Birch 2018-05-15 V1.04                                        */
#/*                                                                         */
#/* Class: Visual                                                           */
#/* Super class, common features of classes which are visual.               */
#/***************************************************************************/



import pygame
import pygame.color
import pygame.freetype
import ELM327



# Events that can occur on a sub classed visual object.
EVENT_MOUSE_DOWN = 1
EVENT_MOUSE_UP = 2
EVENT_MOUSE_MOVE = 3
EVENT_MOUSE_HOVER = 4

# Types of operation when a click is received.
PRESS_NONE = 0
PRESS_DOWN = 1
PRESS_LATCH = 2
PRESS_TOGGLE = 3

# How to align the text on the sub classed visual object.
ALIGN_TEXT_LEFT = 1
ALIGN_TEXT_CENTER = 2
ALIGN_TEXT_RIGHT = 3
ALIGN_TEXT_TOP = 4

# Default margin around elements on the sub classed visual object.
X_MARGIN = 8
Y_MARGIN = 8

# Default button height (and usually width).
BUTTON_HEIGHT = 55


# Which visual items are placed on top of which, from bottom to top.
VisualZOrder = []

# Fonts for visuals.
Fonts = {
	"SmallFontSize" : None,
	"SmallFont" : None,
	"NormalFontSize" : None,
	"NormalFont" : None,
	"LargeFontSize" : None,
	"LargeFont" : None,
	"MassiveFontSize" : None,
	"MassiveFont" : None,
	"HugeFontSize" : None,
	"HugeFont" : None,
}



class Visual:
	def __init__(self, ThisSurface, Name, PressType, xPos, yPos, xLen, yLen, Text, Align = ALIGN_TEXT_CENTER, DownText = ""):
		# Add this new visual instance to the global Z order record. 
		VisualZOrder.append(self)

		# Remember the surface to draw this visual object onto.
		self.ThisSurface = ThisSurface

		# Visual object attributes.
		self.Name = Name
		self.xPos = xPos
		self.yPos = yPos
		self.xLen = xLen
		self.yLen = yLen
		self.SetText(Text)
		self.DownText = DownText
		self.Align = Align
		self.Visible = True
		self.Down = False
		self.PressType = PressType
		self.MouseXPos = xPos
		self.MouseYPos = yPos
		self.Selected = False

		# By default the down text is the same as up text if not specified.
		if self.DownText == "":
			self.DownText = self.Text
		# If image specified, load the image.
		if self.Text[:6] == "IMAGE:":
			self.Image = pygame.image.load(self.Text[6:])
			(self.ImageXLen, self.ImageYLen) = pygame.Surface.get_size(self.Image)
		if self.DownText[:6] == "IMAGE:":
			self.DownImage = pygame.image.load(self.DownText[6:])
			(self.DownImageXLen, self.DownImageYLen) = pygame.Surface.get_size(self.DownImage)

		# Default colours to use on the visual object.
		self.ColourBlack = pygame.Color(0x00, 0x00, 0x00)
		self.ColourGrey = pygame.Color(0x5F, 0x5F, 0x5F)
		self.ColourText = pygame.Color(0x00, 0x00, 0x00)
		self.ColourValueText = pygame.Color(0xAF, 0xAF, 0x00)
		self.ColourBorder = pygame.Color(0x7F, 0x7F, 0x7F)
		self.ColourFillDown = pygame.Color(0x7F, 0xFF, 0xFF)
		self.ColourFillUp = pygame.Color(0x7F, 0x7F, 0xFF)
		self.ColourFill = self.ColourFillUp
		self.ColourDialog = pygame.Color(0x3F, 0xFF, 0x3F)
		self.ColourConfigDialog = pygame.Color(0x3F, 0x3F, 0xFF)

		# Get the dimensions of the surface to draw the visual object onto.
		(self.DisplayXLen, self.DisplayYLen) = pygame.Surface.get_size(self.ThisSurface)



#/********************************************/
#/* Configure the required application font. */
#/********************************************/
	def SetFont(self, FontName):
		# Find a fixed width font, so text can be tabulated.
		FontFile = pygame.freetype.match_font(FontName, True)
		if FontFile == None:
			for FontName in pygame.freetype.get_fonts():
				if FontName.find("mono") > -1:
					FontFile = pygame.freetype.match_font(FontName, True)
					break
		# Configure default font sizes to be used on the visual object.
		Fonts["SmallFontSize"] = int(self.DisplayXLen / 80)
		Fonts["SmallFont"] = pygame.freetype.Font(FontFile, Fonts["SmallFontSize"])
		Fonts["NormalFontSize"] = int(self.DisplayXLen / 60)
		Fonts["NormalFont"] = pygame.freetype.Font(FontFile, Fonts["NormalFontSize"])
		Fonts["NormalFont"].style = pygame.freetype.STYLE_STRONG
		Fonts["LargeFontSize"] = int(self.DisplayXLen / 50)
		Fonts["LargeFont"] = pygame.freetype.Font(FontFile, Fonts["LargeFontSize"])
		Fonts["MassiveFontSize"] = int(self.DisplayXLen / 26)
		Fonts["MassiveFont"] = pygame.freetype.Font(FontFile, Fonts["MassiveFontSize"])
		Fonts["HugeFontSize"] = int(self.DisplayXLen / 23)
		Fonts["HugeFont"] = pygame.freetype.Font(FontFile, Fonts["HugeFontSize"])



#/**************************************************************/
#/* Return the name of the sub classed visual object instance. */
#/**************************************************************/
	def GetName(self):
		return self.Name



#/**************************************************************/
#/* Return the xPos of the sub classed visual object instance. */
#/**************************************************************/
	def GetXPos(self):
		return self.xPos



#/**************************************************************/
#/* Return the yPos of the sub classed visual object instance. */
#/**************************************************************/
	def GetYPos(self):
		return self.yPos



#/**************************************************************/
#/* Return the Text of the sub classed visual object instance. */
#/**************************************************************/
	def GetText(self):
		return self.Text



#/***********************************************************/
#/* Return the visible state of the visual object instance. */
#/***********************************************************/
	def GetVisible(self):
		return self.Visible



#/*************************************************************************/
#/* Return the depressed state of the sub classed visual object instance. */
#/*************************************************************************/
	def GetDown(self):
		return self.Down



#/****************************************************************/
#/* Return press type of the sub classed visual object instance. */
#/****************************************************************/
	def GetPressType(self):
		return self.PressType



#/**********************************************************************/
#/* Set the depressed state of the sub classed visual object instance. */
#/**********************************************************************/
	def SetDown(self, NewDown):
		self.Down = NewDown
		if self.Down == True and self.Text == self.DownText:
			self.ColourFill = self.ColourFillDown
		elif self.Down == False and self.Text == self.DownText:
			self.ColourFill = self.ColourFillUp




#/***************************************************************/
#/* Set the position of the sub classed visual object instance. */
#/***************************************************************/
	def SetPos(self, xPos, yPos):
		self.xPos = xPos
		self.yPos = yPos



#/********************************************************/
#/* Hide or show the sub classed visual object instance. */
#/********************************************************/
	def SetVisible(self, Visible):
		self.Visible = Visible



#/***************************************************/
#/* Format text to be displayed within a set width, */
#/* over a specified number of lines.               */
#/***************************************************/
	def LayoutText(self, DisplayText, DisplayLines, DisplayXLen, DisplayFont):
		Result = ""

		ResultLine = ""
		for Word in DisplayText.split(' '):
			if DisplayFont.get_rect(ResultLine + Word)[2] > DisplayXLen:
				Result += ResultLine[:len(ResultLine) - 1] + "\n"
				ResultLine = Word + " "
			else:
				ResultLine += Word + " "
		if len(ResultLine) > 1:
			Result += ResultLine[:len(ResultLine) - 1]

		return Result



#/***********************************************************/
#/* Set the text on the sub classed visual object instance. */
#/***********************************************************/
	def SetText(self, NewText, Append = False, DataValue = ""):
		if Append == False:
			# Replace the text and try to format the text if possible.
			try:
				self.Text = NewText.format(DataValue)
			except Exception as Catch:
				print(str(Catch))
				self.Text = NewText
		else:
			# Append the text and try to format the text if possible.
			try:
				self.Text += NewText.format(DataValue)
			except Exception as Catch:
				print(str(Catch))
				self.Text += NewText
		# Remove duplicate new line characters from the text.
		self.Text = self.Text.replace('\\n', '\n')
		BeforeText = ""
		while self.Text != BeforeText:
			BeforeText = self.Text
			self.Text = self.Text.replace('\n\n\n', '\n\n')



#/************************************************************************/
#/* Check if an event occurred in this visual area. Perform any required */
#/* actions and let the caller know if the visual area was touched.      */
#/************************************************************************/
	def IsEvent(self, EventType, xPos, yPos, PointerButton, xOffset = 0, yOffset = 0):
		Result = False

		if self.Visible != False:
			# Check if touch occured in the visual area.
			if xPos >= xOffset + self.xPos and xPos <= xOffset + self.xPos + self.xLen and yPos >= yOffset + self.yPos and yPos <= yOffset + self.yPos + self.yLen:
				# Let the caller know what type of event occured.
				if Result == False:
					Result = { "EVENT" : EventType }
				else:
					Result["EVENT"] = EventType

				# Set the background colour of the visual area, for touch and untouch events.
				if EventType == EVENT_MOUSE_DOWN:
					if self.PressType == PRESS_DOWN or self.PressType == PRESS_LATCH:
						self.SetDown(True)
					elif self.PressType == PRESS_TOGGLE:
						if self.GetDown() == False:
							self.SetDown(True)
						else:
							self.SetDown(False)
				elif EventType == EVENT_MOUSE_HOVER:
					self.MouseXPos = xPos
					self.MouseYPos = yPos

		return Result



#/*********************************************/
#/* Draw this button on the provided surface. */
#/*********************************************/
	def Display(self, ThisSurface, xOffset = 0, yOffset = 0):
		if self.Visible == True:
			if self.Text[:6] == "IMAGE:" and self.Down == False:
				ScaledPng = pygame.transform.scale(self.Image, (BUTTON_HEIGHT - 7, BUTTON_HEIGHT - 7))
				ThisSurface.blit(ScaledPng, (xOffset + self.xPos + (self.xLen - BUTTON_HEIGHT + 7) / 2, yOffset + self.yPos + (self.yLen - BUTTON_HEIGHT + 7) / 2))
			elif self.DownText[:6] == "IMAGE:" and self.Down == True:
				ScaledPng = pygame.transform.scale(self.DownImage, (BUTTON_HEIGHT - 7, BUTTON_HEIGHT - 7))
				ThisSurface.blit(ScaledPng, (xOffset + self.xPos + (self.xLen - BUTTON_HEIGHT + 7) / 2, yOffset + self.yPos + (self.yLen - BUTTON_HEIGHT + 7) / 2))
			else:
				# Select the required text to display.
				if self.Down == False:
					self.DisplayText = self.Text
				else:
					self.DisplayText = self.DownText
				# Draw each line of the text onto the specified surface.
				yTop = yOffset
				LineCount = 1
				TextLines = self.DisplayText.split('\n')
				for TextLine in TextLines:
					# Split the formatting text from the display text.
					TextFormat = TextLine.split('|')
					ThisText = TextFormat[ELM327.FIELD_PID_DESCRIPTION]
					FontWidth = Fonts["LargeFont"].get_rect(ThisText)[2]
					FontHeight = Fonts["LargeFont"].get_rect(ThisText)[3]
					FontGap = FontHeight + Y_MARGIN

					# Calculate the location of the text on the surface, depending on the specified alignment.
					if self.Align == ALIGN_TEXT_LEFT:
						TextXPos = xOffset + X_MARGIN + self.xPos
						TextYPos = yOffset + Y_MARGIN + self.yPos
					elif self.Align == ALIGN_TEXT_CENTER:
						TextXPos = xOffset + self.xPos + self.xLen / 2 - FontWidth / 2
						TextYPos = yOffset + self.yPos + self.yLen / 2 - FontHeight / 2
					elif self.Align == ALIGN_TEXT_RIGHT:
						TextXPos = xOffset + self.xPos + self.xLen - FontWidth + X_MARGIN
						TextYPos = yOffset + Y_MARGIN + self.yPos
					elif self.Align == ALIGN_TEXT_TOP:
						TextXPos = xOffset + self.xPos + self.xLen / 2 - FontWidth / 2
						TextYPos = yOffset + Y_MARGIN + self.yPos

					# If left alignment has been specified, draw a fient line between each line of text.
					if self.Align == ALIGN_TEXT_LEFT:
						pygame.draw.line(self.ThisSurface, self.ColourGrey, (X_MARGIN + self.xPos + xOffset, self.yPos + yOffset + Y_MARGIN / 2), (self.xPos + self.xLen - 2 * X_MARGIN - xOffset, self.yPos + yOffset + Y_MARGIN / 2), 1)
						# Check for item number currently selected.
						if self.MouseXPos >= X_MARGIN + self.xPos + xOffset and self.MouseXPos <= TextXPos + self.xLen - 3 * X_MARGIN - xOffset and self.MouseYPos >= TextYPos and self.MouseYPos <= TextYPos + FontHeight:
							self.Selected = LineCount
							# Highlight currently selected item.
							pygame.draw.rect(self.ThisSurface, self.ColourFillDown, (X_MARGIN + self.xPos + xOffset, self.yPos + yOffset + Y_MARGIN / 2, self.xLen - 3 * X_MARGIN - xOffset, FontGap), 0)

					# Display the text on the surface.
					RenderText = Fonts["LargeFont"].render(ThisText, self.ColourText)
					ThisSurface.blit(RenderText[0], (TextXPos, TextYPos))

					# If format text also supplied, display right aligned on the surface.
					if len(TextFormat) > ELM327.FIELD_PID_FORMAT_1:
						ThisText = TextFormat[ELM327.FIELD_PID_FORMAT_1]
						if len(TextFormat) > ELM327.FIELD_PID_FORMAT_2:
							ThisText += " " + TextFormat[ELM327.FIELD_PID_FORMAT_2]
						TextXPos = xOffset + self.xPos + self.xLen - Fonts["LargeFont"].get_rect(ThisText)[2] - X_MARGIN
						TextYPos = yOffset + Y_MARGIN + self.yPos
						RenderText = Fonts["LargeFont"].render(ThisText, self.ColourText)
						ThisSurface.blit(RenderText[0], (TextXPos, TextYPos))

					# Add to the vertial offset, so the next displayed line is displayed below the current line.
					yOffset += FontGap
					# Don't display text outside of the visual area.
					if yOffset + FontGap >= self.yLen:
						break
					LineCount += 1

