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
#/* Class: Gadgit                                                           */
#/* Display value data in various visual formats. Such as meter,            */
#/* vertial bar, horizontal bar, info...                                    */
#/***************************************************************************/


import math
import pygame
import pygame.color
import pygame.freetype
import Visual
import Button


class Gadgit(Visual.Visual):
	# Selectable styles of a gague.
	STYLE_GAGUE = 0
	STYLE_VERTICAL_BAR = 1
	STYLE_HORIZONTAL_BAR = 2
	STYLE_TEXT = 3
	STYLE_END = 4



	def __init__(self, ThisSurface, Name, xPos, yPos, xLen, yLen, Text, Align = Visual.Visual.ALIGN_TEXT_CENTER):
		Visual.Visual.__init__(self, ThisSurface, Name, xPos, yPos, xLen, yLen, Text, Align)

		# Buttons displayed on a gague.
		self.Buttons = {
			"SELECT" : Button.Button(self.ThisSurface, "SELECT", 0, 0, 50, 50, "SELECT"),
			"SWITCH" : Button.Button(self.ThisSurface, "SWITCH", (xLen - 50) * 2/6, 0, 50, 50, "SWITCH"),
			"DRAG" : Button.Button(self.ThisSurface, "DRAG", (xLen - 50) * 4/6, 0, 50, 50, "DRAG"),
			"CLOSE" : Button.Button(self.ThisSurface, "CLOSE", xLen - 50, 0, 50, 50, "CLOSE"),
		}

		# Attributes applied to the various styles of gague.
		self.StyleAttrib = {
			self.STYLE_GAGUE : {
				"LABEL" : Text,
				"WIDTH" : xLen,
				"HEIGHT" : yLen,
				"POINTER_WIDTH" : 6,
				"LABEL_COLOUR" : pygame.Color(0xFF, 0xFF, 0x00),
				"VALUE_COLOUR" : pygame.Color(0x00, 0x00, 0x7F),
				"POINTER_COLOUR" : pygame.Color(0x7F, 0x00, 0x00),
				"BACKGROUND_COLOUR" : pygame.Color(0x5F, 0x5F, 0x5F),
				"BAR_COLOUR" : pygame.Color(0x00, 0xFF, 0x00),
				"BAR_HIGH_COLOUR" : pygame.Color(0xFF, 0x00, 0x00),
				"FILL_COLOUR" : pygame.Color(0xFF, 0xFF, 0xFF)
			},
			self.STYLE_VERTICAL_BAR : {
				"LABEL" : Text,
				"WIDTH" : xLen / 3,
				"HEIGHT" : yLen,
				"POINTER_WIDTH" : 3,
				"LABEL_COLOUR" : pygame.Color(0x00, 0x00, 0x7F),
				"VALUE_COLOUR" : pygame.Color(0x00, 0x00, 0x7F),
				"POINTER_COLOUR" : pygame.Color(0xFF, 0x7F, 0x7F),
				"BACKGROUND_COLOUR" : pygame.Color(0x00, 0x00, 0x00),
				"BAR_COLOUR" : pygame.Color(0x00, 0xFF, 0x00),
				"BAR_HIGH_COLOUR" : pygame.Color(0xFF, 0x00, 0x00),
				"FILL_COLOUR" : pygame.Color(0x5F, 0x5F, 0x5F)
			},
			self.STYLE_HORIZONTAL_BAR : {
				"LABEL" : Text,
				"WIDTH" : xLen,
				"HEIGHT" : yLen / 3,
				"POINTER_WIDTH" : 3,
				"LABEL_COLOUR" : pygame.Color(0x00, 0x00, 0x7F),
				"VALUE_COLOUR" : pygame.Color(0x00, 0x00, 0x7F),
				"POINTER_COLOUR" : pygame.Color(0xFF, 0x7F, 0x7F),
				"BACKGROUND_COLOUR" : pygame.Color(0x00, 0x00, 0x00),
				"BAR_COLOUR" : pygame.Color(0x00, 0xFF, 0x00),
				"BAR_HIGH_COLOUR" : pygame.Color(0xFF, 0x00, 0x00),
				"FILL_COLOUR" : pygame.Color(0x5F, 0x5F, 0x5F)
			},
			self.STYLE_TEXT : {
				"LABEL" : Text,
				"WIDTH" : xLen,
				"HEIGHT" : yLen / 3,
				"POINTER_WIDTH" : 3,
				"LABEL_COLOUR" : pygame.Color(0xFF, 0xFF, 0x00),
				"VALUE_COLOUR" : pygame.Color(0xFF, 0xFF, 0x00),
				"POINTER_COLOUR" : pygame.Color(0xFF, 0x7F, 0x7F),
				"BACKGROUND_COLOUR" : pygame.Color(0x00, 0x00, 0x00),
				"BAR_COLOUR" : pygame.Color(0x00, 0xFF, 0x00),
				"BAR_HIGH_COLOUR" : pygame.Color(0xFF, 0x00, 0x00),
				"FILL_COLOUR" : pygame.Color(0x5F, 0x5F, 0x5F)
			},
		}

		# ECU PID associated with this gague.
		self.PID = ""
		self.PidDescription = ""

		# Attributes of this gague.
		self.Style = self.STYLE_GAGUE
		self.ValueMin = 0
		self.ValueHigh = 80
		self.ValueMax = 100
		self.Value = 0

		# Appy the initial default style to the gague.
		self.SetStyle()



#/************************************************************************/
#/* Check if an event occurred in this gagues area. Perform any required */
#/* actions and let the caller know if the gague was touched.            */
#/************************************************************************/
	def IsEvent(self, EventType, xPos, yPos, PointerButton, xOffset = 0, yOffset = 0):
		self.Result = Visual.Visual.IsEvent(self, EventType, xPos, yPos, PointerButton, xOffset, yOffset)

		# Handle gague events.
		if self.Result != False:
			# Tell caller the name of the gague that was touched.
			self.Result["GADGIT"] = self.Name
			# Tell caller the name of the button on the gague that was touched.
			self.Result["BUTTON"] = ""
			for ThisButton in self.Buttons:
				self.ButtonResult = self.Buttons[ThisButton].IsEvent(EventType, xPos, yPos, PointerButton, self.xPos, self.yPos)
				if self.ButtonResult != False:
					self.Result["BUTTON"] = ThisButton
					break

			if EventType == Visual.Visual.EVENT_MOUSE_DOWN:
				# If Switch button was pressed, switch the style of the gague.
				if self.Result["BUTTON"] == "SWITCH":
					self.Style += 1
					if self.Style >= self.STYLE_END:
						self.Style = 0
					self.SetStyle()
			elif EventType == Visual.Visual.EVENT_MOUSE_MOVE:
				# If Drag button dragged, drag the gague to the new location.
				if self.Result["BUTTON"] == "DRAG":
					self.SetPos(xPos - (self.xLen - 25) * 4/6, yPos - 25)

		return self.Result



#/**********************************************/
#/* Return the PID associated with this gague. */
#/**********************************************/
	def GetPID(self):
		return self.PID



#/*******************************************/
#/* Set the PID associated with this gague. */
#/*******************************************/
	def SetPID(self, PID, PidDescription):
		self.PID = PID
		self.PidDescription = PidDescription



#/*************************************/
#/* Set the data value of this gague. */
#/*************************************/
	def SetData(self, PidData):
		self.Value = PidData



#/********************************/
#/* Set the style of this gague. */
#/********************************/
	def SetStyle(self):
		self.xLen = self.StyleAttrib[self.Style]["WIDTH"]
		self.yLen = self.StyleAttrib[self.Style]["HEIGHT"]
		self.PointerWidth = self.StyleAttrib[self.Style]["POINTER_WIDTH"]
		self.ColourText = self.StyleAttrib[self.Style]["LABEL_COLOUR"]
		self.ColourValue = self.StyleAttrib[self.Style]["VALUE_COLOUR"]
		self.BackgroundColour = self.StyleAttrib[self.Style]["BACKGROUND_COLOUR"]
		self.PointerColour = self.StyleAttrib[self.Style]["POINTER_COLOUR"]
		self.BarColour = self.StyleAttrib[self.Style]["BAR_COLOUR"]
		self.BarHighColour = self.StyleAttrib[self.Style]["BAR_HIGH_COLOUR"]
		self.FillColour = self.StyleAttrib[self.Style]["FILL_COLOUR"]



#/*********************************************/
#/* Draw this gadgit on the provided surface. */
#/*********************************************/
	def Display(self, ThisSurface, xOffset = 0, yOffset = 0):
		# Calculate the ratio value to display on which ever style gague is displayed.
		self.PointerRatio = (0.000001 + self.Value - self.ValueMin) / (self.ValueMax - self.ValueMin)
		self.PointerHighRatio = (0.000001 + self.ValueHigh - self.ValueMin) / (self.ValueMax - self.ValueMin)
		# Erase the background.
		pygame.draw.rect(ThisSurface, self.BackgroundColour, (self.xPos, self.yPos, self.xLen, self.yLen), 0)
		# Display a border around the full area.
		pygame.draw.rect(ThisSurface, self.ColourBorder, (self.xPos, self.yPos, self.xLen, self.yLen), 1)

		# Draw the gague as a clock gague.
		if self.Style == self.STYLE_GAGUE:
			# Calculate center of gague area.
			OriginX = int(self.X_MARGIN + self.xPos + (self.xLen - 2*self.X_MARGIN) / 2)
			OriginY = int(self.Y_MARGIN + self.yPos + (self.xLen - 2*self.X_MARGIN) / 2)
			Radius = int(self.xLen / 2 - 2 * self.X_MARGIN)

			# Draw gague background.
			pygame.draw.circle(self.ThisSurface, self.FillColour, (OriginX, OriginY), Radius, 0)
			pygame.draw.circle(self.ThisSurface, pygame.Color(0x00, 0x00, 0x00), (OriginX, OriginY), Radius, 2)
			pygame.draw.circle(self.ThisSurface, pygame.Color(0x00, 0x00, 0x00), (OriginX, OriginY), 20, 0)

			# Draw gague values.
			self.TextLabels = self.PidDescription.split("|")

			self.ThisText = self.TextLabels[0]
			self.TextHeight = self.LargeFont.get_rect(self.ThisText)[3]
			self.TextXPos = self.xPos + (self.xLen - self.LargeFont.get_rect(self.ThisText)[2]) / 2
			self.TextYPos = self.yPos + self.yLen - self.Y_MARGIN - self.TextHeight
			RenderText = self.LargeFont.render(self.ThisText, self.ColourText)
			ThisSurface.blit(RenderText[0], (self.TextXPos, self.TextYPos))

			self.ThisText = self.TextLabels[1].format(self.Value)
			self.TextXPos = self.xPos + (self.xLen - self.MassiveFont.get_rect(self.ThisText)[2]) / 2
			self.TextYPos = self.yPos + (self.yLen - self.MassiveFont.get_rect(self.ThisText)[3]) * 3 / 4
			RenderText = self.MassiveFont.render(self.ThisText, self.ColourValue)
			ThisSurface.blit(RenderText[0], (self.TextXPos, self.TextYPos))

			# Draw gague pointer.
			PointerX = (Radius - 20) * math.sin((math.pi / 180) * (-360 * self.PointerRatio))
			PointerY = (Radius - 20) * math.cos((math.pi / 180) * (-360 * self.PointerRatio))
			pygame.draw.line(self.ThisSurface, self.PointerColour, (OriginX, OriginY), (OriginX + PointerX, OriginY + PointerY), self.PointerWidth)
			PointerX = 40 * math.sin((math.pi / 180) * (-360 * self.PointerRatio + 180))
			PointerY = 40 * math.cos((math.pi / 180) * (-360 * self.PointerRatio + 180))
			pygame.draw.line(self.ThisSurface, self.PointerColour, (OriginX, OriginY), (OriginX + PointerX, OriginY + PointerY), self.PointerWidth)

		# Draw the gague as a vertical bar gague.
		elif self.Style == self.STYLE_VERTICAL_BAR:
			# Draw gague background.
			pygame.draw.rect(ThisSurface, self.FillColour, (self.X_MARGIN + self.xPos, self.Y_MARGIN + self.yPos, self.xLen - 2 * self.X_MARGIN, self.yLen - 2 * self.Y_MARGIN), 0)
			# Draw gague pointer.
			self.PointerYPos = self.Y_MARGIN + self.yPos + int((self.yLen - 2 * self.Y_MARGIN) - (self.yLen - 2 * self.Y_MARGIN) * self.PointerRatio)
			self.PointerYHighPos = self.Y_MARGIN + self.yPos + int((self.yLen - 2 * self.Y_MARGIN) - (self.yLen - 2 * self.Y_MARGIN) * self.PointerHighRatio)
			pygame.draw.rect(ThisSurface, self.BarColour, (self.X_MARGIN + self.xPos, self.PointerYPos, self.xLen - 2 * self.X_MARGIN, self.yPos + self.yLen - self.Y_MARGIN - self.PointerYPos), 0)
			if self.Value >= self.ValueHigh:
				pygame.draw.rect(ThisSurface, self.BarHighColour, (self.X_MARGIN + self.xPos, self.PointerYPos, self.xLen - 2 * self.X_MARGIN, self.PointerYHighPos - self.PointerYPos), 0)
			pygame.draw.line(self.ThisSurface, self.PointerColour, (self.X_MARGIN + self.xPos, self.PointerYPos), (self.xPos + self.xLen - self.X_MARGIN - self.PointerWidth / 2, self.PointerYPos), self.PointerWidth)

			# Draw gague values.
			self.TextLabels = self.PidDescription.split("|")

			self.ThisText = self.TextLabels[0]
			self.TextHeight = self.LargeFont.get_rect(self.ThisText)[3]
			self.TextXPos = self.xPos + self.xLen - self.X_MARGIN - self.TextHeight
			self.TextYPos = self.yPos + (self.yLen - self.LargeFont.get_rect(self.ThisText)[2]) / 2
			RenderText = self.LargeFont.render(self.ThisText, self.ColourText, rotation = 90)
			ThisSurface.blit(RenderText[0], (self.TextXPos, self.TextYPos))

			self.ThisText = self.TextLabels[1].format(self.Value)
			self.TextXPos = self.xPos + (self.xLen - self.HugeFont.get_rect(self.ThisText)[3]) / 2
			self.TextYPos = self.yPos + (self.yLen - self.HugeFont.get_rect(self.ThisText)[2]) / 2
			RenderText = self.HugeFont.render(self.ThisText, self.ColourValue, rotation = 90)
			ThisSurface.blit(RenderText[0], (self.TextXPos, self.TextYPos))

		# Draw the gague as a horizontal bar gague.
		elif self.Style == self.STYLE_HORIZONTAL_BAR:
			# Draw gague background.
			pygame.draw.rect(ThisSurface, self.FillColour, (self.X_MARGIN + self.xPos, self.Y_MARGIN + self.yPos, self.xLen - 2 * self.X_MARGIN, self.yLen - 2 * self.Y_MARGIN), 0)
			# Draw gague pointer.
			self.PointerXPos = self.X_MARGIN + self.xPos + int((self.xLen - 2 * self.X_MARGIN) * self.PointerRatio)
			self.PointerHighXPos = self.X_MARGIN + self.xPos + int((self.xLen - 2 * self.X_MARGIN) * self.PointerHighRatio)
			pygame.draw.rect(ThisSurface, self.BarColour, (self.X_MARGIN + self.xPos, self.Y_MARGIN + self.yPos, self.PointerXPos - self.X_MARGIN - self.xPos, self.yLen - 2 * self.Y_MARGIN), 0)
			if self.Value >= self.ValueHigh:
				pygame.draw.rect(ThisSurface, self.BarHighColour, (self.PointerXPos, self.Y_MARGIN + self.yPos, self.PointerHighXPos - self.PointerXPos, self.yLen - 2 * self.Y_MARGIN), 0)
			pygame.draw.line(self.ThisSurface, self.PointerColour, (self.PointerXPos, self.yPos + self.Y_MARGIN), (self.PointerXPos, self.yPos + self.yLen - self.Y_MARGIN - self.PointerWidth / 2), self.PointerWidth)

			# Draw gague values.
			self.TextLabels = self.PidDescription.split("|")

			self.ThisText = self.TextLabels[0]
			self.TextHeight = self.LargeFont.get_rect(self.ThisText)[3]
			self.TextXPos = self.xPos + (self.xLen - self.LargeFont.get_rect(self.ThisText)[2]) / 2
			self.TextYPos = self.yPos + self.yLen - self.Y_MARGIN - self.TextHeight
			RenderText = self.LargeFont.render(self.ThisText, self.ColourText)
			ThisSurface.blit(RenderText[0], (self.TextXPos, self.TextYPos))

			self.ThisText = self.TextLabels[1].format(self.Value)
			self.TextXPos = self.xPos + (self.xLen - self.HugeFont.get_rect(self.ThisText)[2]) / 2
			self.TextYPos = self.yPos + (self.yLen - self.HugeFont.get_rect(self.ThisText)[3]) / 2
			RenderText = self.HugeFont.render(self.ThisText, self.ColourValue)
			ThisSurface.blit(RenderText[0], (self.TextXPos, self.TextYPos))

		# Draw the gague as text only.
		elif self.Style == self.STYLE_TEXT:
			# Draw gague background.
			pygame.draw.rect(ThisSurface, self.FillColour, (self.X_MARGIN + self.xPos, self.Y_MARGIN + self.yPos, self.xLen - 2 * self.X_MARGIN, self.yLen - 2 * self.Y_MARGIN), 0)
			# Draw gague values.
			self.TextLabels = self.PidDescription.split("|")

			self.ThisText = self.TextLabels[0]
			self.TextHeight = self.LargeFont.get_rect(self.ThisText)[3]
			self.TextXPos = self.xPos + (self.xLen - self.LargeFont.get_rect(self.ThisText)[2]) / 2
			self.TextYPos = self.yPos + self.yLen - self.Y_MARGIN - self.TextHeight
			RenderText = self.LargeFont.render(self.ThisText, self.ColourText)
			ThisSurface.blit(RenderText[0], (self.TextXPos, self.TextYPos))

			self.ThisText = self.TextLabels[1].format(self.Value)
			self.TextXPos = self.xPos + (self.xLen - self.HugeFont.get_rect(self.ThisText)[2]) / 2
			self.TextYPos = self.yPos + (self.yLen - self.HugeFont.get_rect(self.ThisText)[3]) / 2
			RenderText = self.HugeFont.render(self.ThisText, self.ColourValue)
			ThisSurface.blit(RenderText[0], (self.TextXPos, self.TextYPos))

		# Display all buttons on the gadgit.
		for ThisButton in self.Buttons:
			self.Buttons[ThisButton].Display(self.ThisSurface, self.xPos, self.yPos)

