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
#/* Class: Gadgit                                                           */
#/* Display value data in various visual formats. Such as meter,            */
#/* vertial bar, horizontal bar, info...                                    */
#/***************************************************************************/



import math
import pygame
import pygame.color
import pygame.freetype
import ELM327
import Visual
import Button



# Selectable styles of a gague.
STYLE_GAGUE = 0
STYLE_VERTICAL_BAR = 1
STYLE_HORIZONTAL_BAR = 2
STYLE_TEXT = 3
STYLE_END = 4



class Gadgit(Visual.Visual):
	def __init__(self, ThisSurface, Name, PressType, xPos, yPos, xLen, yLen, Text, Align = Visual.ALIGN_TEXT_CENTER):
		Visual.Visual.__init__(self, ThisSurface, Name, PressType, xPos, yPos, xLen, yLen, Text, Align)

		# Buttons displayed on a gague.
		self.Buttons = {
			"SELECT" : Button.Button(self.ThisSurface, "SELECT", Visual.PRESS_DOWN, 0, 0, Visual.BUTTON_HEIGHT, Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Select.png"),
			"SWITCH" : Button.Button(self.ThisSurface, "SWITCH", Visual.PRESS_DOWN, (xLen - Visual.BUTTON_HEIGHT) * 2/6, 0, Visual.BUTTON_HEIGHT, Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Switch.png"),
			"DRAG" : Button.Button(self.ThisSurface, "DRAG", Visual.PRESS_DOWN, (xLen - Visual.BUTTON_HEIGHT) * 4/6, 0, Visual.BUTTON_HEIGHT, Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Drag.png"),
			"CLOSE" : Button.Button(self.ThisSurface, "CLOSE", Visual.PRESS_DOWN, xLen - Visual.BUTTON_HEIGHT, 0, Visual.BUTTON_HEIGHT, Visual.BUTTON_HEIGHT, "IMAGE:ICONS/Close.png"),
		}

		# Attributes applied to the various styles of gague.
		self.StyleAttrib = {
			STYLE_GAGUE : {
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
			STYLE_VERTICAL_BAR : {
				"LABEL" : Text,
				"WIDTH" : xLen / 4,
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
			STYLE_HORIZONTAL_BAR : {
				"LABEL" : Text,
				"WIDTH" : xLen,
				"HEIGHT" : yLen / 4,
				"POINTER_WIDTH" : 3,
				"LABEL_COLOUR" : pygame.Color(0x00, 0x00, 0x7F),
				"VALUE_COLOUR" : pygame.Color(0x00, 0x00, 0x7F),
				"POINTER_COLOUR" : pygame.Color(0xFF, 0x7F, 0x7F),
				"BACKGROUND_COLOUR" : pygame.Color(0x00, 0x00, 0x00),
				"BAR_COLOUR" : pygame.Color(0x00, 0xFF, 0x00),
				"BAR_HIGH_COLOUR" : pygame.Color(0xFF, 0x00, 0x00),
				"FILL_COLOUR" : pygame.Color(0x5F, 0x5F, 0x5F)
			},
			STYLE_TEXT : {
				"LABEL" : Text,
				"WIDTH" : xLen,
				"HEIGHT" : yLen / 4,
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
		self.Style = STYLE_GAGUE
		self.ValueMin = 0
		self.ValueHigh = 80
		self.ValueMax = 100
		self.Value = 0

		# Appy the initial default style to the gague.
		self.SetStyle(self.Style)



#/************************************************************************/
#/* Check if an event occurred in this gagues area. Perform any required */
#/* actions and let the caller know if the gague was touched.            */
#/************************************************************************/
	def IsEvent(self, EventType, xPos, yPos, PointerButton, xOffset = 0, yOffset = 0):
		Result = Visual.Visual.IsEvent(self, EventType, xPos, yPos, PointerButton, xOffset, yOffset)

		# Handle gague events.
		if Result != False:
			# Tell caller the name of the gague that was touched.
			Result["GADGIT"] = self.Name
			# Tell caller the name of the button on the gague that was touched.
			Result["BUTTON"] = ""
			for ThisButton in self.Buttons:
				ButtonResult = self.Buttons[ThisButton].IsEvent(EventType, xPos, yPos, PointerButton, self.xPos, self.yPos)
				if ButtonResult != False:
					Result["BUTTON"] = ThisButton
					break

			if EventType == Visual.EVENT_MOUSE_DOWN:
				# If Switch button was pressed, switch the style of the gague.
				if Result["BUTTON"] == "SWITCH":
					self.Style += 1
					if self.Style >= STYLE_END:
						self.Style = 0
					self.SetStyle(self.Style)
			elif EventType == Visual.EVENT_MOUSE_MOVE:
				# If Drag button dragged, drag the gague to the new location.
				if Result["BUTTON"] == "DRAG":
					self.SetPos(xPos - self.xLen / 2, yPos - self.yLen / 2)

		return Result



#/**********************************************/
#/* Return the PID associated with this gague. */
#/**********************************************/
	def GetPID(self):
		return self.PID



#/***************************************************/
#/* Return the style ID associated with this gague. */
#/***************************************************/
	def GetStyle(self):
		return self.Style



#/*******************************************/
#/* Set the PID associated with this gague. */
#/*******************************************/
	def SetPID(self, PID, PidDescription):
		self.PID = PID
		self.PidDescription = PidDescription
		ValueDefinition = self.PidDescription.split("|")
		if len(ValueDefinition) > ELM327.FIELD_PID_MIN_1:
			self.ValueMin = float(ValueDefinition[ELM327.FIELD_PID_MIN_1])
		else:
			self.ValueMin = 0
		if len(ValueDefinition) > ELM327.FIELD_PID_MAX_1:
			self.ValueMax = float(ValueDefinition[ELM327.FIELD_PID_MAX_1])
		else:
			self.ValueMax = 100
		if len(ValueDefinition) > ELM327.FIELD_PID_HIGH_1:
			self.ValueHigh = float(ValueDefinition[ELM327.FIELD_PID_HIGH_1])
		else:
			self.ValueHigh = 0



#/*************************************/
#/* Set the data value of this gague. */
#/*************************************/
	def SetData(self, PidData):
		self.Value = PidData



#/*******************************************************/
#/* Set the min, max and high data range of this gague. */
#/*******************************************************/
	def SetDataRange(self, ValueMin, ValueHigh, ValueMax):
		self.ValueMin = float(ValueMin)
		self.ValueHigh = float(ValueHigh)
		self.ValueMax = float(ValueMax)



#/********************************/
#/* Set the style of this gague. */
#/********************************/
	def SetStyle(self, Style):
		self.Style = Style

		# Apply currently selected gadgit style.
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

		# Arrange buttons so they don't clash in any gadgit type.
		self.Buttons["DRAG"].SetPos((self.xLen - Visual.BUTTON_HEIGHT) / 2, (self.yLen - Visual.BUTTON_HEIGHT) / 2)
		self.Buttons["CLOSE"].SetPos(self.xLen - Visual.BUTTON_HEIGHT, 0)
		if self.Style == STYLE_VERTICAL_BAR:
			self.Buttons["SWITCH"].SetPos((self.xLen - Visual.BUTTON_HEIGHT) / 2, Visual.BUTTON_HEIGHT)
			self.Buttons["SELECT"].SetPos((self.xLen - Visual.BUTTON_HEIGHT) / 2, self.yLen - 2 * Visual.BUTTON_HEIGHT)
		else:
			self.Buttons["SWITCH"].SetPos(Visual.BUTTON_HEIGHT, (self.yLen - Visual.BUTTON_HEIGHT) / 2)
			self.Buttons["SELECT"].SetPos(self.xLen - 2 * Visual.BUTTON_HEIGHT, (self.yLen - Visual.BUTTON_HEIGHT) / 2)



#/*********************************************/
#/* Draw this gadgit on the provided surface. */
#/*********************************************/
	def Display(self, ThisSurface, xOffset = 0, yOffset = 0):
		try:
			ThisValue = self.Value
			if type(ThisValue) is tuple:
				ThisValue = float(ThisValue[0])
			else:
				ThisValue = float(ThisValue)
		except:
			ThisValue = 0
		# Calculate the ratio value to display on which ever style gague is displayed.
		PointerRatio = (0.000001 + ThisValue - self.ValueMin) / (self.ValueMax - self.ValueMin)
		PointerHighRatio = (0.000001 + self.ValueHigh - self.ValueMin) / (self.ValueMax - self.ValueMin)
		# Erase the background.
		pygame.draw.rect(ThisSurface, self.BackgroundColour, (self.xPos, self.yPos, self.xLen, self.yLen), 0)
		# Display a border around the full area.
		pygame.draw.rect(ThisSurface, self.ColourBorder, (self.xPos, self.yPos, self.xLen, self.yLen), 1)

		# Draw the gague as a clock gague.
		if self.Style == STYLE_GAGUE:
			# Calculate center of gague area.
			OriginX = int(Visual.X_MARGIN + self.xPos + (self.xLen - 2*Visual.X_MARGIN) / 2)
			OriginY = int(Visual.Y_MARGIN + self.yPos + (self.xLen - 2*Visual.X_MARGIN) / 2)
			Radius = int(self.xLen / 2 - 2 * Visual.X_MARGIN)

			# Draw gague background.
			pygame.draw.circle(self.ThisSurface, self.FillColour, (OriginX, OriginY), Radius, 0)
			pygame.draw.circle(self.ThisSurface, self.ColourBlack, (OriginX, OriginY), Radius, 2)
			pygame.draw.circle(self.ThisSurface, self.ColourBlack, (OriginX, OriginY), 20, 0)
			pygame.draw.arc(self.ThisSurface, self.BarHighColour, (4*Visual.X_MARGIN + self.xPos, 4*Visual.Y_MARGIN + self.yPos, self.xLen - 8*Visual.X_MARGIN, self.xLen - 8*Visual.Y_MARGIN), -2*math.pi - 0.6*math.pi/2, 2*math.pi * -PointerHighRatio - math.pi/2, 2*Visual.X_MARGIN)
			for Angle in range(0, 100, 10):
				AngleX1 = (Radius - 10) * math.sin((math.pi / 180) * (-360 * Angle/100))
				AngleY1 = (Radius - 10) * math.cos((math.pi / 180) * (-360 * Angle/100))
				AngleX2 = (Radius - 30) * math.sin((math.pi / 180) * (-360 * Angle/100))
				AngleY2 = (Radius - 30) * math.cos((math.pi / 180) * (-360 * Angle/100))
				AngleX3 = (Radius - 70) * math.sin((math.pi / 180) * (-360 * Angle/100))
				AngleY3 = (Radius - 70) * math.cos((math.pi / 180) * (-360 * Angle/100))
				if Angle == 0:
					TickWidth = 10
				else:
					TickWidth = 5
				pygame.draw.line(self.ThisSurface, self.ColourBlack, (OriginX + AngleX1, OriginY + AngleY1), (OriginX + AngleX2, OriginY + AngleY2), TickWidth)
				ThisText = "{:0.2f}".format(((self.ValueMax - self.ValueMin) / 100 * Angle) + self.ValueMin)
				RenderText = Visual.Fonts["NormalFont"].render(ThisText, self.ColourBlack)
				ThisSurface.blit(RenderText[0], (OriginX + AngleX3 - Visual.Fonts["NormalFont"].get_rect(ThisText)[2] / 2, OriginY + AngleY3))


			# Draw gague values.
			TextLabels = self.PidDescription.split("|")

			DisplayText = self.LayoutText(TextLabels[ELM327.FIELD_PID_DESCRIPTION], 2, self.xLen - 4 * Visual.X_MARGIN, Visual.Fonts["LargeFont"])
			DisplayTextOffset = 0
			for DisplayTextLine in DisplayText.split('\n'):
				ThisText = DisplayTextLine
				TextHeight = Visual.Fonts["LargeFont"].get_rect(ThisText)[3]
				TextXPos = self.xPos + (self.xLen - Visual.Fonts["LargeFont"].get_rect(ThisText)[2]) / 2
				TextYPos = DisplayTextOffset + self.yPos + self.yLen - Visual.Y_MARGIN - 2*(TextHeight + Visual.Y_MARGIN)
				RenderText = Visual.Fonts["LargeFont"].render(ThisText, self.ColourText)
				ThisSurface.blit(RenderText[0], (TextXPos, TextYPos))
				DisplayTextOffset += TextHeight + Visual.Y_MARGIN

			if len(TextLabels) > 1 and TextLabels[ELM327.FIELD_PID_FORMAT_1].find("f}") > -1:
				ThisFormat = TextLabels[ELM327.FIELD_PID_FORMAT_1]
				if ThisFormat.find('[') > -1:
					ThisFormat = ThisFormat[:ThisFormat.find('[')] + ThisFormat[ThisFormat.find(']')+1:]
				ThisText = ThisFormat.format(ThisValue)
				TextXPos = self.xPos + (self.xLen - Visual.Fonts["MassiveFont"].get_rect(ThisText)[2]) / 2
				TextYPos = self.yPos + (self.yLen - Visual.Fonts["MassiveFont"].get_rect(ThisText)[3]) * 3 / 5
				RenderText = Visual.Fonts["MassiveFont"].render(ThisText, self.ColourValue)
				ThisSurface.blit(RenderText[0], (TextXPos, TextYPos))

			# Draw gague pointer.
			PointerX = (Radius - 20) * math.sin((math.pi / 180) * (-360 * PointerRatio))
			PointerY = (Radius - 20) * math.cos((math.pi / 180) * (-360 * PointerRatio))
			pygame.draw.line(self.ThisSurface, self.PointerColour, (OriginX, OriginY), (OriginX + PointerX, OriginY + PointerY), self.PointerWidth)
			PointerX = 40 * math.sin((math.pi / 180) * (-360 * PointerRatio + 180))
			PointerY = 40 * math.cos((math.pi / 180) * (-360 * PointerRatio + 180))
			pygame.draw.line(self.ThisSurface, self.PointerColour, (OriginX, OriginY), (OriginX + PointerX, OriginY + PointerY), self.PointerWidth)

		# Draw the gague as a vertical bar gague.
		elif self.Style == STYLE_VERTICAL_BAR:
			# Draw gague background.
			pygame.draw.rect(ThisSurface, self.FillColour, (Visual.X_MARGIN + self.xPos, Visual.Y_MARGIN + self.yPos, self.xLen - 2 * Visual.X_MARGIN, self.yLen - 2 * Visual.Y_MARGIN), 0)
			# Draw gague pointer.
			PointerYPos = Visual.Y_MARGIN + self.yPos + int((self.yLen - 2 * Visual.Y_MARGIN) - (self.yLen - 2 * Visual.Y_MARGIN) * PointerRatio)
			PointerYHighPos = Visual.Y_MARGIN + self.yPos + int((self.yLen - 2 * Visual.Y_MARGIN) - (self.yLen - 2 * Visual.Y_MARGIN) * PointerHighRatio)
			pygame.draw.rect(ThisSurface, self.BarColour, (Visual.X_MARGIN + self.xPos, PointerYPos, self.xLen - 2 * Visual.X_MARGIN, self.yPos + self.yLen - Visual.Y_MARGIN - PointerYPos), 0)
			if ThisValue >= self.ValueHigh:
				pygame.draw.rect(ThisSurface, self.BarHighColour, (Visual.X_MARGIN + self.xPos, PointerYPos, self.xLen - 2 * Visual.X_MARGIN, PointerYHighPos - PointerYPos), 0)
			pygame.draw.line(self.ThisSurface, self.PointerColour, (Visual.X_MARGIN + self.xPos, PointerYPos), (self.xPos + self.xLen - Visual.X_MARGIN - self.PointerWidth / 2, PointerYPos), self.PointerWidth)

			# Draw gague values.
			TextLabels = self.PidDescription.split("|")

			DisplayText = self.LayoutText(TextLabels[ELM327.FIELD_PID_DESCRIPTION], 2, self.yLen - 4 * Visual.Y_MARGIN, Visual.Fonts["LargeFont"])
			DisplayTextOffset = 0
			for DisplayTextLine in DisplayText.split('\n'):
				ThisText = DisplayTextLine
				TextHeight = Visual.Fonts["LargeFont"].get_rect(ThisText)[3]
				TextXPos = DisplayTextOffset + self.xPos + self.xLen - 2*(TextHeight + Visual.X_MARGIN)
				TextYPos = self.yPos + (self.yLen - Visual.Fonts["LargeFont"].get_rect(ThisText)[2]) / 2
				RenderText = Visual.Fonts["LargeFont"].render(ThisText, self.ColourText, rotation = 90)
				ThisSurface.blit(RenderText[0], (TextXPos, TextYPos))
				DisplayTextOffset += TextHeight + Visual.Y_MARGIN

			if len(TextLabels) > 1 and TextLabels[ELM327.FIELD_PID_FORMAT_1].find("f}") > -1:
				ThisFormat = TextLabels[ELM327.FIELD_PID_FORMAT_1]
				if ThisFormat.find('[') > -1:
					ThisFormat = ThisFormat[:ThisFormat.find('[')] + ThisFormat[ThisFormat.find(']')+1:]
				ThisText = ThisFormat.format(ThisValue)
				TextXPos = self.xPos + (self.xLen - Visual.Fonts["HugeFont"].get_rect(ThisText)[3]) / 5
				TextYPos = self.yPos + (self.yLen - Visual.Fonts["HugeFont"].get_rect(ThisText)[2]) / 2
				RenderText = Visual.Fonts["HugeFont"].render(ThisText, self.ColourValue, rotation = 90)
				ThisSurface.blit(RenderText[0], (TextXPos, TextYPos))

		# Draw the gague as a horizontal bar gague.
		elif self.Style == STYLE_HORIZONTAL_BAR:
			# Draw gague background.
			pygame.draw.rect(ThisSurface, self.FillColour, (Visual.X_MARGIN + self.xPos, Visual.Y_MARGIN + self.yPos, self.xLen - 2 * Visual.X_MARGIN, self.yLen - 2 * Visual.Y_MARGIN), 0)
			# Draw gague pointer.
			PointerXPos = Visual.X_MARGIN + self.xPos + int((self.xLen - 2 * Visual.X_MARGIN) * PointerRatio)
			PointerHighXPos = Visual.X_MARGIN + self.xPos + int((self.xLen - 2 * Visual.X_MARGIN) * PointerHighRatio)
			pygame.draw.rect(ThisSurface, self.BarColour, (Visual.X_MARGIN + self.xPos, Visual.Y_MARGIN + self.yPos, PointerXPos - Visual.X_MARGIN - self.xPos, self.yLen - 2 * Visual.Y_MARGIN), 0)
			if ThisValue >= self.ValueHigh:
				pygame.draw.rect(ThisSurface, self.BarHighColour, (PointerXPos, Visual.Y_MARGIN + self.yPos, PointerHighXPos - PointerXPos, self.yLen - 2 * Visual.Y_MARGIN), 0)
			pygame.draw.line(self.ThisSurface, self.PointerColour, (PointerXPos, self.yPos + Visual.Y_MARGIN), (PointerXPos, self.yPos + self.yLen - Visual.Y_MARGIN - self.PointerWidth / 2), self.PointerWidth)

			# Draw gague values.
			TextLabels = self.PidDescription.split("|")

			DisplayText = self.LayoutText(TextLabels[ELM327.FIELD_PID_DESCRIPTION], 2, self.xLen - 4 * Visual.X_MARGIN, Visual.Fonts["LargeFont"])
			DisplayTextOffset = 0
			for DisplayTextLine in DisplayText.split('\n'):
				ThisText = DisplayTextLine
				TextHeight = Visual.Fonts["LargeFont"].get_rect(ThisText)[3]
				TextXPos = self.xPos + (self.xLen - Visual.Fonts["LargeFont"].get_rect(ThisText)[2]) / 2
				TextYPos = DisplayTextOffset + self.yPos + self.yLen - 2*(TextHeight + Visual.Y_MARGIN)
				RenderText = Visual.Fonts["LargeFont"].render(ThisText, self.ColourText)
				ThisSurface.blit(RenderText[0], (TextXPos, TextYPos))
				DisplayTextOffset += TextHeight + Visual.X_MARGIN

			if len(TextLabels) > 1 and TextLabels[ELM327.FIELD_PID_FORMAT_1].find("f}") > -1:
				ThisFormat = TextLabels[ELM327.FIELD_PID_FORMAT_1]
				if ThisFormat.find('[') > -1:
					ThisFormat = ThisFormat[:ThisFormat.find('[')] + ThisFormat[ThisFormat.find(']')+1:]
				ThisText = ThisFormat.format(ThisValue)
				TextXPos = self.xPos + (self.xLen - Visual.Fonts["HugeFont"].get_rect(ThisText)[2]) / 2
				TextYPos = self.yPos + (self.yLen - Visual.Fonts["HugeFont"].get_rect(ThisText)[3]) / 5
				RenderText = Visual.Fonts["HugeFont"].render(ThisText, self.ColourValue)
				ThisSurface.blit(RenderText[0], (TextXPos, TextYPos))

		# Draw the gague as text only.
		elif self.Style == STYLE_TEXT:
			# Draw gague background.
			pygame.draw.rect(ThisSurface, self.FillColour, (Visual.X_MARGIN + self.xPos, Visual.Y_MARGIN + self.yPos, self.xLen - 2 * Visual.X_MARGIN, self.yLen - 2 * Visual.Y_MARGIN), 0)
			# Draw gague values.
			TextLabels = self.PidDescription.split("|")

			DisplayText = self.LayoutText(TextLabels[ELM327.FIELD_PID_DESCRIPTION], 2, self.xLen - 4 * Visual.X_MARGIN, Visual.Fonts["LargeFont"])
			DisplayTextOffset = 0
			for DisplayTextLine in DisplayText.split('\n'):
				ThisText = DisplayTextLine
				TextHeight = Visual.Fonts["LargeFont"].get_rect(ThisText)[3]
				TextXPos = self.xPos + (self.xLen - Visual.Fonts["LargeFont"].get_rect(ThisText)[2]) / 2
				TextYPos = DisplayTextOffset + self.yPos + self.yLen - Visual.Y_MARGIN - 2*(TextHeight + Visual.Y_MARGIN)
				RenderText = Visual.Fonts["LargeFont"].render(ThisText, self.ColourText)
				ThisSurface.blit(RenderText[0], (TextXPos, TextYPos))
				DisplayTextOffset += TextHeight + Visual.Y_MARGIN

			if len(TextLabels) > 1:
				if TextLabels[ELM327.FIELD_PID_FORMAT_1].find("f}") > -1:
					ThisFormat = TextLabels[ELM327.FIELD_PID_FORMAT_1]
					if ThisFormat.find('[') > -1:
						ThisFormat = ThisFormat[:ThisFormat.find('[')] + ThisFormat[ThisFormat.find(']')+1:]
					ThisText = ThisFormat.format(ThisValue)
				else:
					ThisText = str(self.Value)
				TextXPos = self.xPos + (self.xLen - Visual.Fonts["HugeFont"].get_rect(ThisText)[2]) / 2
				TextYPos = self.yPos + (self.yLen - Visual.Fonts["HugeFont"].get_rect(ThisText)[3]) / 5
				RenderText = Visual.Fonts["HugeFont"].render(ThisText, self.ColourValue)
				ThisSurface.blit(RenderText[0], (TextXPos, TextYPos))

		# Display the PID number in top left.
		ThisText = self.PID
		TextHeight = Visual.Fonts["SmallFont"].get_rect(ThisText)[3]
		TextXPos = self.xPos + Visual.X_MARGIN
		TextYPos = self.yPos + Visual.Y_MARGIN
		RenderText = Visual.Fonts["SmallFont"].render(ThisText, self.ColourBlack)
		ThisSurface.blit(RenderText[0], (TextXPos, TextYPos))

		# Display all buttons on the gadgit.
		for ThisButton in self.Buttons:
			self.Buttons[ThisButton].Display(self.ThisSurface, self.xPos, self.yPos)

