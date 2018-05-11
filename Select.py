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
#/* (C) Jason Birch 2018-05-09 V1.03                                        */
#/*                                                                         */
#/* Class: Select                                                           */
#/* Display a dialog showing a list of text and get the line number of the  */
#/* text which the user click on.                                           */
#/***************************************************************************/



import pygame
import Visual
import Button



class Select(Visual.Visual):
	def __init__(self, ThisSurface, Name, Text):
		# Select covers full display surface to prevent other interface items being clicked before the selection has been clicked.
		Visual.Visual.__init__(self, ThisSurface, Name, Visual.PRESS_NONE, 0, 0, Visual.BUTTON_HEIGHT, Visual.BUTTON_HEIGHT, Text)

		# Select covers full display, but only draw in middle so some interface can still be seen, but not used.
		self.xLen = self.DisplayXLen
		self.yLen = self.DisplayYLen
		self.ConfirmXLen = self.DisplayXLen / 1.5
		self.ConfirmYLen = self.DisplayYLen / 1.5
		self.ConfirmXOffset = (self.xLen - self.ConfirmXLen) / 2
		self.ConfirmYOffset = (self.yLen - self.ConfirmYLen) / 1.65
		self.Align = Visual.ALIGN_TEXT_LEFT
		self.ColourFill = self.ColourDialog
		
		# Buttons displayed on the confirm dialog.
		self.Buttons = {
			"CLOSE" : Button.Button(self.ThisSurface, "CLOSE", Visual.PRESS_DOWN, self.ConfirmXOffset + self.ConfirmXLen - Visual.BUTTON_HEIGHT, self.ConfirmYOffset, Visual.BUTTON_HEIGHT, Visual.BUTTON_HEIGHT, "IMAGE:Icons/Close.png"),
		}



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
				if ButtonResult != False:
					Result["BUTTON"] = ThisButton
					break
			if Result["BUTTON"] == "":
				if EventType == Visual.EVENT_MOUSE_DOWN:
					if self.Selected != False:
						Result["SELECTED"] = self.Selected

		else:
			# Always return true, no other user interface is available until this dialog answered.
			Result["BUTTON"] = ""

		return Result



#/*********************************************/
#/* Draw this dialog on the provided surface. */
#/*********************************************/
	def Display(self, ThisSurface, xOffset = 0, yOffset = 0):
		# Display dialog background and border.
		pygame.draw.rect(ThisSurface, self.ColourFill, (xOffset + self.ConfirmXOffset, yOffset + self.ConfirmYOffset, self.ConfirmXLen, self.ConfirmYLen), 0)
		pygame.draw.rect(ThisSurface, self.ColourBorder, (xOffset + self.ConfirmXOffset, yOffset + self.ConfirmYOffset, self.ConfirmXLen, self.ConfirmYLen), 4)

		# Draw any super class elements.
		Visual.Visual.Display(self, ThisSurface, Visual.X_MARGIN + self.ConfirmXOffset, Visual.Y_MARGIN + self.ConfirmYOffset, self.ConfirmXLen, self.ConfirmYOffset + self.ConfirmYLen)

		# Display all buttons on the gadgit.
		for ThisButton in self.Buttons:
			self.Buttons[ThisButton].Display(self.ThisSurface, self.xPos, self.yPos)

