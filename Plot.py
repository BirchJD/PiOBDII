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
#/* Class: Plot                                                             */
#/* Plot a history of selected value data over time.                        */
#/***************************************************************************/


import pygame
import Visual
import Button


class Plot(Visual.Visual):
	def __init__(self, ThisSurface, Name, xPos, yPos, xLen, yLen, Text):
		Visual.Visual.__init__(self, ThisSurface, Name, xPos, yPos, xLen, yLen, Text)



#/**********************************************************************/
#/* Check if an event occurred in this plot area. Perform any required */
#/* actions and let the caller know if the plot area was touched.      */
#/**********************************************************************/
	def IsEvent(self, EventType, xPos, yPos, PointerButton, xOffset = 0, yOffset = 0):
		self.Result = Visual.Visual.IsEvent(self, EventType, xPos, yPos, PointerButton, xOffset, yOffset)
		if self.Result != False:
			self.Result["BUTTON"] = self.Name
		return self.Result



#/************************************************/
#/* Draw this plot area on the provided surface. */
#/************************************************/
	def Display(self, ThisSurface):
		pygame.draw.rect(ThisSurface, self.ColourFill, (self.xPos, self.yPos, self.xLen, self.yLen), 0)
		pygame.draw.rect(ThisSurface, self.ColourBorder, (self.xPos, self.yPos, self.xLen, self.yLen), 1)

