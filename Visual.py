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
#/* Class: Visual                                                           */
#/* Super class, common features of classes which are visual.               */
#/***************************************************************************/


import pygame
import pygame.color
import pygame.freetype


class Visual:
	# Events that can occur on a sub classed visual object.
	EVENT_MOUSE_DOWN = 1
	EVENT_MOUSE_UP = 2
	EVENT_MOUSE_MOVE = 3

	# How to align the text on the sub classed visual object.
	ALIGN_TEXT_LEFT = 1
	ALIGN_TEXT_CENTER = 2
	ALIGN_TEXT_RIGHT = 3

	# Default margin around elements on the sub classed visual object.
	X_MARGIN = 8
	Y_MARGIN = 8



	def __init__(self, ThisSurface, Name, xPos, yPos, xLen, yLen, Text, Align = ALIGN_TEXT_CENTER):
		# Remember the surface to draw this visual object onto.
		self.ThisSurface = ThisSurface

		# Visual object attributes.
		self.Name = Name
		self.xPos = xPos
		self.yPos = yPos
		self.xLen = xLen
		self.yLen = yLen
		self.Text = Text
		self.Align = Align

		# Default colours to use on the visual object.
		self.ColourText = pygame.Color(0x00, 0x00, 0x00)
		self.ColourBorder = pygame.Color(0x7F, 0x7F, 0x7F)
		self.ColourFillDown = pygame.Color(0x7F, 0xFF, 0xFF)
		self.ColourFillUp = pygame.Color(0x7F, 0x7F, 0xFF)
		self.ColourFill = self.ColourFillUp

		# Get the dimensions of the surface to draw the visual object onto.
		(self.DisplayXLen, self.DisplayYLen) = pygame.Surface.get_size(self.ThisSurface)

		# Find a fixed width font, so text can be tabulated.
		self.FontName = "freemono"
		self.FontFile = pygame.freetype.match_font(self.FontName, True)
		if self.FontFile == None:
			for self.FontName in pygame.freetype.get_fonts():
				if self.FontName.find("mono") > -1:
					self.FontFile = pygame.freetype.match_font(self.FontName, True)
					break

		# Configure default font sizes to be used on the visual object.
		self.LargeFontSize = int(self.DisplayXLen / 80)
		self.LargeFont = pygame.freetype.Font(self.FontFile, self.LargeFontSize)
		self.MassiveFontSize = int(self.DisplayXLen / 40)
		self.MassiveFont = pygame.freetype.Font(self.FontFile, self.MassiveFontSize)
		self.HugeFontSize = int(self.DisplayXLen / 20)
		self.HugeFont = pygame.freetype.Font(self.FontFile, self.HugeFontSize)



#/**************************************************************/
#/* Return the name of the sub classed visual object instance. */
#/**************************************************************/
	def GetName(self):
		return self.Name



#/***************************************************************/
#/* Set the position of the sub classed visual object instance. */
#/***************************************************************/
	def SetPos(self, xPos, yPos):
		self.xPos = xPos
		self.yPos = yPos



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



#/************************************************************************/
#/* Check if an event occurred in this visual area. Perform any required */
#/* actions and let the caller know if the visual area was touched.      */
#/************************************************************************/
	def IsEvent(self, EventType, xPos, yPos, PointerButton, xOffset = 0, yOffset = 0):
		self.Result = False

		# Check if touch occured in the visual area.
		if xPos >= xOffset + self.xPos and xPos <= xOffset + self.xPos + self.xLen and yPos >= yOffset + self.yPos and yPos <= yOffset + self.yPos + self.yLen:
			# Let the caller know what type of event occured.
			if self.Result == False:
				self.Result = { "EVENT" : EventType }
			else:
				self.Result["EVENT"] = EventType

			# Set the background colour of the visual area, for touch and untouch events.
			if EventType == self.EVENT_MOUSE_DOWN:
				self.ColourFill = self.ColourFillDown
			elif EventType == self.EVENT_MOUSE_UP:
				self.ColourFill = self.ColourFillUp

		return self.Result



#/*********************************************/
#/* Draw this button on the provided surface. */
#/*********************************************/
	def Display(self, ThisSurface, xOffset = 0, yOffset = 0):
		# Remove duplicate new line characters from the text.
		self.Text = self.Text.replace('\\n', '\n')
		self.Text = self.Text.replace('\n\n\n', '\n\n')

		# Draw each line of the text onto the specified surface.
		self.TextLines = self.Text.split('\n')
		for TextLine in self.TextLines:
			# Split the formatting text from the display text.
			TextFormat = TextLine.split('|')

			self.ThisText = TextFormat[0]

			# Calculate the location of the text on the surface, depending on the specified alignment.
			if self.Align == self.ALIGN_TEXT_LEFT:
				self.TextXPos = self.X_MARGIN + self.xPos
				self.TextYPos = self.Y_MARGIN + self.yPos
			elif self.Align == self.ALIGN_TEXT_CENTER:
				self.TextXPos = self.xPos + self.xLen / 2 - self.LargeFont.get_rect(self.ThisText)[2] / 2
				self.TextYPos = self.yPos + self.yLen / 2 - self.LargeFont.get_rect(self.ThisText)[3] / 2
			if self.Align == self.ALIGN_TEXT_RIGHT:
				self.TextXPos = self.xPos + self.xLen - self.LargeFont.get_rect(self.ThisText)[2] + self.X_MARGIN
				self.TextYPos = self.Y_MARGIN + self.yPos

			# Display the text on the surface.
			RenderText = self.LargeFont.render(self.ThisText, self.ColourText)
			ThisSurface.blit(RenderText[0], (xOffset + self.TextXPos, yOffset + self.TextYPos))

			# If format text also supplied, display right aligned on the surface.
			if len(TextFormat) > 1:
				self.ThisText = TextFormat[1]

				self.TextXPos = self.xPos + self.xLen - self.LargeFont.get_rect(self.ThisText)[2] - self.X_MARGIN
				self.TextYPos = self.Y_MARGIN + self.yPos

				RenderText = self.LargeFont.render(self.ThisText, self.ColourText)
				ThisSurface.blit(RenderText[0], (xOffset + self.TextXPos, yOffset + self.TextYPos))

			# If left alignment has been specified, draw a fient line between each line of text.
			if self.Align == self.ALIGN_TEXT_LEFT:
				pygame.draw.line(self.ThisSurface, self.ColourBorder, (self.X_MARGIN + self.xPos, self.yPos + yOffset + self.Y_MARGIN / 2), (self.xPos + self.xLen - 2 * self.X_MARGIN, self.yPos + yOffset + self.Y_MARGIN / 2), 1)

			# Add to the vertial offset, so the next displayed line is displayed below the current line.
			yOffset += self.LargeFont.get_rect(self.ThisText)[3] + self.Y_MARGIN

