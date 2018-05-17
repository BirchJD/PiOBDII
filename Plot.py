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
#/* Class: Plot                                                             */
#/* Plot a history of selected value data over time.                        */
#/***************************************************************************/



import os
import datetime
import pygame
import Visual
import Button
import ELM327



PLOT_COUNT = 3
PLOT_POINTS = 512
PLOT_WIDTH = 2



class Plot(Visual.Visual):
	def __init__(self, ThisSurface, Name, PressType, xPos, yPos, xLen, yLen, Text):
		Visual.Visual.__init__(self, ThisSurface, Name, PressType, xPos, yPos, xLen, yLen, Text)

		self.ClearConfig()



#/****************************************************/
#/* Get the PID associated with the specified index. */
#/****************************************************/
	def GetPID(self, PlotIndex):
		return self.PID[PlotIndex]



#/*******************************************/
#/* Set the PID associated with this gague. */
#/*******************************************/
	def SetPID(self, PlotIndex, PID, PidDescription):
		self.PID[PlotIndex] = PID
		ValueDefinition = PidDescription.split("|")
		self.PidDescription[PlotIndex] = PidDescription
		if len(ValueDefinition) > ELM327.FIELD_PID_MIN_1:
			self.PlotAttrib[PlotIndex]["ValueMin"] = float(ValueDefinition[ELM327.FIELD_PID_MIN_1])
		else:
			self.PlotAttrib[PlotIndex]["ValueMin"] = 0
		if len(ValueDefinition) > ELM327.FIELD_PID_MAX_1:
			self.PlotAttrib[PlotIndex]["ValueMax"] = float(ValueDefinition[ELM327.FIELD_PID_MAX_1])
		else:
			self.PlotAttrib[PlotIndex]["ValueMax"] = 100
		if len(ValueDefinition) > ELM327.FIELD_PID_HIGH_1:
			self.PlotAttrib[PlotIndex]["ValueHigh"] = float(ValueDefinition[ELM327.FIELD_PID_HIGH_1])
		else:
			self.PlotAttrib[PlotIndex]["ValueHigh"] = 0



#/***********************************/
#/* Set the data value of a series. */
#/***********************************/
	def SetData(self, Index, PidData):
		# Check for X axis label conditions and create X axis label when met.
		ThisAxisTime = datetime.datetime.now()
		if int(self.LastAxisTime.minute/2) != int(ThisAxisTime.minute/2):
			self.LastAxisTime = ThisAxisTime
			self.xAxisLabels[self.PlotIndex[Index]] = ThisAxisTime.strftime("%H:%M")
		# Store provided data.
		if type(PidData) is not str and type(PidData) is not tuple:
			self.PlotPoints[Index][self.PlotIndex[Index]] = PidData
		else:
			self.PlotPoints[Index][self.PlotIndex[Index]] = 0
		if self.PlotIndex[Index] < PLOT_POINTS:
			self.PlotIndex[Index] += 1



#/********************************/
#/* Is the data aquisition full? */
#/********************************/
	def IsDataEnd(self, Index):
		return (self.PlotIndex[Index] == PLOT_POINTS - 1)



#/***********************************/
#/* Clear all series configuration. */
#/***********************************/
	def ClearConfig(self):
		self.ClearData()
		# ECU PID associated with each plot.
		self.PID = [ "", "", "" ]
		self.PidDescription = [ "", "", "" ]
		self.PlotAttrib = [ {}, {}, {} ]
		# Attributes of each plot.
		for Index in range(PLOT_COUNT):
			self.PlotAttrib[Index] = {
				"Colour" : pygame.Color(0x7F * 2**(8*(Index+1)) + 0xFF),
				"ValueMin" : 0,
				"ValueHigh" : 80,
				"ValueMax" : 100,
				"Value" : 0,
			}



#/************************************************/
#/* Clear all plot data to start a new data log. */
#/************************************************/
	def ClearData(self):
		self.LastAxisTime = datetime.datetime.now()
		self.xAxisLabels = {}
		self.PlotIndex = [ 0, 0, 0 ]
		self.PlotPoints = [ [0] * PLOT_POINTS, [0] * PLOT_POINTS, [0] * PLOT_POINTS ]



#/**********************************************************************/
#/* Check if an event occurred in this plot area. Perform any required */
#/* actions and let the caller know if the plot area was touched.      */
#/**********************************************************************/
	def IsEvent(self, EventType, xPos, yPos, PointerButton, xOffset = 0, yOffset = 0):
		Result = Visual.Visual.IsEvent(self, EventType, xPos, yPos, PointerButton, xOffset, yOffset)
		if Result != False:
			Result["BUTTON"] = self.Name
		return Result



#/*******************************************/
#/* Load gadgits onto meters tab from disk. */
#/*******************************************/
	def LoadSeriesConfig(self, ValidPIDs):
		try:
			self.ClearConfig()
			if os.path.isfile("CONFIG/PLOT_SERIES.CFG"):
				File = open("CONFIG/PLOT_SERIES.CFG", 'r')
				Index = 0
				TextLine = "."
				while TextLine != "":
					TextLine = File.readline()
					TextLine = TextLine.replace("\n", "")
					TextElements = TextLine.split('|')
					for ThisElement in TextElements:
						if ThisElement[:4] == "PID=":
							ThisPID = str(ThisElement[4:])
							ThisPidDescription = ""
							if ThisPID in ValidPIDs:
								ThisPidDescription = ValidPIDs[ThisPID]
							self.SetPID(Index, ThisPID, ThisPidDescription)
							Index += 1
				File.close()
		except:
			# On fail remove all loaded series.
			self.ClearConfig()



#/*******************************/
#/* Save series config to disk. */
#/*******************************/
	def SaveSeriesConfig(self):
		File = open("CONFIG/PLOT_SERIES.CFG", 'w')
		for Index in range(PLOT_COUNT):
			Data = "PID=" + str(self.PID[Index])
			File.write(Data + "\n")
		File.close()



#/************************************************/
#/* Draw this plot area on the provided surface. */
#/************************************************/
	def Display(self, ThisSurface):
		# Draw background.
		pygame.draw.rect(ThisSurface, self.ColourFill, (self.xPos, self.yPos, self.xLen, self.yLen), 0)
		pygame.draw.rect(ThisSurface, self.ColourBorder, (self.xPos, self.yPos, self.xLen, self.yLen), 1)
		# Draw Y axis dividers.
		yAxisScale = int(self.yLen - 2*Visual.Y_MARGIN)
		yAxisStep = int(yAxisScale / 10)
		for yOffset in range(0, yAxisScale, yAxisStep):
			pygame.draw.line(ThisSurface, self.ColourGrey, (self.xPos + Visual.X_MARGIN, self.yPos + self.yLen - yOffset), (self.xPos + self.xLen - 2*Visual.X_MARGIN, self.yPos + self.yLen - yOffset), 1)
		# Display data scale.
		xStep = (self.xLen - 2*Visual.X_MARGIN) / PLOT_POINTS
		for Index in self.xAxisLabels:
			ThisText = self.xAxisLabels[Index]
			TextHeight = Visual.Fonts["NormalFont"].get_rect(ThisText)[3]
			TextXPos = self.xPos + Index * xStep
			TextYPos = self.yPos + self.yLen - TextHeight - Visual.Y_MARGIN
			RenderText = Visual.Fonts["NormalFont"].render(ThisText, self.ColourBlack)
			ThisSurface.blit(RenderText[0], (Visual.X_MARGIN + TextXPos, TextYPos))
			pygame.draw.line(ThisSurface, self.ColourGrey, (TextXPos, self.yPos + Visual.Y_MARGIN), (TextXPos, self.yPos + self.yLen - 2*Visual.Y_MARGIN), 1)

		# Plot all series.
		DisplayTextOffset = 0
		for Index in range(PLOT_COUNT):
			# Display series description.
			TextLabels = self.PidDescription[Index].split("|")
			ThisText = "[" + str(Index+1) + "] " + self.PID[Index] + " " + TextLabels[ELM327.FIELD_PID_DESCRIPTION]
			if len(TextLabels) > ELM327.FIELD_PID_FORMAT_1 and TextLabels[ELM327.FIELD_PID_FORMAT_1].find("f}") > -1:
				ThisText += " " + TextLabels[ELM327.FIELD_PID_FORMAT_1].format(self.PlotPoints[Index][self.PlotIndex[Index] - 1])
				TextHeight = Visual.Fonts["LargeFont"].get_rect(ThisText)[3]
				TextXPos = Visual.X_MARGIN
				TextYPos = DisplayTextOffset + Visual.Y_MARGIN + self.yPos
				RenderText = Visual.Fonts["LargeFont"].render(ThisText, self.PlotAttrib[Index]["Colour"])
				ThisSurface.blit(RenderText[0], (TextXPos, TextYPos))
				DisplayTextOffset += TextHeight + Visual.Y_MARGIN

				# Plot series scale.
				yScale = (self.yLen - 2*Visual.Y_MARGIN) / (self.PlotAttrib[Index]["ValueMax"] - self.PlotAttrib[Index]["ValueMin"])
				xStep = (self.xLen - 2*Visual.X_MARGIN) / PLOT_POINTS
				# Display Y axis scale values.
				for yOffset in range(0, yAxisScale - yAxisStep, yAxisStep):
					ThisText = TextLabels[ELM327.FIELD_PID_FORMAT_1].format(yOffset / yScale + self.PlotAttrib[Index]["ValueMin"])
					TextWidth = Visual.Fonts["NormalFont"].get_rect(ThisText)[2]
					TextHeight = Visual.Fonts["NormalFont"].get_rect(ThisText)[3]
					TextXPos = self.xPos + self.xLen - TextWidth - Visual.X_MARGIN
					TextYPos = self.yPos + self.yLen - yOffset - (3 - Index) * (TextHeight + 2)
					RenderText = Visual.Fonts["NormalFont"].render(ThisText, self.PlotAttrib[Index]["Colour"])
					ThisSurface.blit(RenderText[0], (TextXPos, TextYPos))
				# Plot series.
				xOffset = 0
				for PlotIndex in range(self.PlotIndex[Index] - 1):
					PlotX1 = Visual.X_MARGIN + xOffset
					PlotY1 = self.yPos + self.yLen - Visual.Y_MARGIN - yScale * (self.PlotPoints[Index][PlotIndex] - self.PlotAttrib[Index]["ValueMin"])
					PlotX2 = Visual.X_MARGIN + xOffset + xStep
					PlotY2 = self.yPos + self.yLen - Visual.Y_MARGIN - yScale * (self.PlotPoints[Index][PlotIndex+1] - self.PlotAttrib[Index]["ValueMin"])
					pygame.draw.line(ThisSurface, self.PlotAttrib[Index]["Colour"], (PlotX1, PlotY1), (PlotX2, PlotY2), PLOT_WIDTH)
					xOffset += xStep

