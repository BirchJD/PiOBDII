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
#/* (C) Jason Birch 2018-05-29 V1.09                                        */
#/*                                                                         */
#/* Class: ELM327                                                           */
#/* Handle communications with an ELM327 device, communicating with the     */
#/* CAN BUS on a car ECU.                                                   */
#/***************************************************************************/



import time
import serial


DEBUG = "OFF"

# Connection to ELM327 device status.
CONNECT_SUCCESS = 0
CONNECT_ELM327_FAIL = 1
CONNECT_CAN_BUS_FAIL = 2

# Serial port constants.
SERIAL_PORT_NAME = None
#SERIAL_PORT_BAUD = 115200
#SERIAL_PORT_BAUD = 57600
SERIAL_PORT_BAUD = 38400
#SERIAL_PORT_BAUD = 9600
SERIAL_PORT_TIME_OUT = 7
SERIAL_LINEFEED_TYPE = b'\r'
#SERIAL_LINEFEED_TYPE = b'\r\n'

# ELM327 Device related constants.
ELM_RESET_PERIOD = 1
ELM_CONNECT_SETTLE_PERIOD = 5

# Constant string responses.
STRING_NOT_IMPLEMENTED = "!NOT IMPLEMENTED!"
STRING_NO_DATA = "N/A"
STRING_ERROR = "!ERROR!"
STRING_TODO = ":TODO:"
STRING_INVALID = "[INVALID]"
STRING_NO_DESCRIPTION = "[NO DESCRIPTION]"

# Data fields.
FIELD_PID_DESCRIPTION = 0
FIELD_PID_FORMAT_1 = 1
FIELD_PID_MIN_1 = 2
FIELD_PID_MAX_1 = 3
FIELD_PID_HIGH_1 = 4
FIELD_PID_FORMAT_2 = 5
FIELD_PID_MIN_2 = 6
FIELD_PID_MAX_2 = 7
FIELD_PID_HIGH_2 = 8



# PID Numbers and their function pointers implemented in this class.
PidFunctions = {}



class ELM327:
	def __init__(self):
		self.InitResult = ""
		self.ValidPIDs = {}
		self.ValidFreezePIDs = {}
		self.MilOn = False
		self.FreezeFrameCount = 0

#  /*************************************************/
# /* Read Vehicle OBD Standards lookup table data. */
#/*************************************************/
		self.VehicleObdStandards = {}
		try:
			with open("DATA/VehicleObdStandards.txt") as ThisFile:
				for ThisLine in ThisFile:
					Digit, Code = ThisLine.partition(" ")[::2]
					self.VehicleObdStandards[Digit] = Code.strip()
		except Exception as Catch:
			print(STRING_ERROR + " DATA/VehicleObdStandards.txt : " + str(Catch))
			self.InitResult += "FAILED TO READ FILE: DATA/VehicleObdStandards.txt\n"

#  /**********************************************************/
# /* Read Commanded Secondary Air Status lookup table data. */
#/**********************************************************/
		self.CommandedSecondaryAirStatus = {}
		try:
			with open("DATA/CommandedSecondaryAirStatus.txt") as ThisFile:
				for ThisLine in ThisFile:
					Digit, Code = ThisLine.partition(" ")[::2]
					self.CommandedSecondaryAirStatus[Digit] = Code.strip()
		except Exception as Catch:
			print(STRING_ERROR + " DATA/CommandedSecondaryAirStatus.txt : " + str(Catch))
			self.InitResult += "FAILED TO READ FILE: DATA/CommandedSecondaryAirStatus.txt\n"

#  /**********************************************/
# /* Read Fuel System Status lookup table data. */
#/**********************************************/
		self.FuelSystemStatus = {}
		try:
			with open("DATA/FuelSystemStatus.txt") as ThisFile:
				for ThisLine in ThisFile:
					Digit, Code = ThisLine.partition(" ")[::2]
					self.FuelSystemStatus[Digit] = Code.strip()
		except Exception as Catch:
			print(STRING_ERROR + " DATA/FuelSystemStatus.txt : " + str(Catch))
			self.InitResult += "FAILED TO READ FILE: DATA/FuelSystemStatus.txt\n"

#  /**********************************************/
# /* Read OBDII Trouble Code lookup table data. */
#/**********************************************/
		self.TroubleCodePrefix = {}
		try:
			with open("DATA/TroubleCodePrefix.txt") as ThisFile:
				for ThisLine in ThisFile:
					Digit, Code = ThisLine.partition(" ")[::2]
					self.TroubleCodePrefix[Digit] = Code.strip()
		except Exception as Catch:
			print(STRING_ERROR + " DATA/TroubleCodePrefix.txt : " + str(Catch))
			self.InitResult += "FAILED TO READ FILE: DATA/TroubleCodePrefix.txt\n"

#  /**********************************************************/
# /* Read OBDII Trouble Code Description lookup table data. */
#/**********************************************************/
		self.LoadVehicle("DATA/TroubleCodes-R53_Cooper_S.txt")

#  /***************************************************/
# /* Read Mode 01 PID description lookup table data. */
#/***************************************************/
		self.PidDescriptionsMode01 = {}
		try:
			with open("DATA/PidDescriptionsMode01.txt") as ThisFile:
				for ThisLine in ThisFile:
					Digit, Code = ThisLine.partition(" ")[::2]
					self.PidDescriptionsMode01[Digit] = Code.strip()
		except:
			self.InitResult += "FAILED TO READ FILE: DATA/PidDescriptionsMode01.txt\n"

#  /***************************************************/
# /* Read Mode 05 PID description lookup table data. */
#/***************************************************/
		self.PidDescriptionsMode05 = {}
		try:
			with open("DATA/PidDescriptionsMode05.txt") as ThisFile:
				for ThisLine in ThisFile:
					Digit, Code = ThisLine.partition(" ")[::2]
					self.PidDescriptionsMode05[Digit] = Code.strip()
		except:
			self.InitResult += "FAILED TO READ FILE: DATA/PidDescriptionsMode05.txt\n"

#  /***************************************************/
# /* Read Mode 09 PID description lookup table data. */
#/***************************************************/
		self.PidDescriptionsMode09 = {}
		try:
			with open("DATA/PidDescriptionsMode09.txt") as ThisFile:
				for ThisLine in ThisFile:
					Digit, Code = ThisLine.partition(" ")[::2]
					self.PidDescriptionsMode09[Digit] = Code.strip()
		except:
			self.InitResult += "FAILED TO READ FILE: DATA/PidDescriptionsMode09.txt\n"



	def __del__(self):
		# Close the ELM327 device after use.
		self.Close()



#/******************************************************/
#/* Load the trouble codes for the configured vehicle. */
#/******************************************************/
	def LoadVehicle(self, VehicleFile):
		self.TroubleCodeDescriptions = {}
		# Load the ISO/SAE Trouble Code Descriptions.
		try:
			with open("DATA/TroubleCodes-ISO-SAE.txt") as ThisFile:
				for ThisLine in ThisFile:
					Code, Description = ThisLine.partition(" ")[::2]
					self.TroubleCodeDescriptions[Code] = Description.strip()
		except Exception as Catch:
			print(STRING_ERROR + " DATA/TroubleCodes-ISO-SAE.txt : " + str(Catch))
			self.InitResult += "FAILED TO READ FILE: DATA/TroubleCodes-ISO-SAE.txt\n"

		# Load the Vehicle/Manufacturer Trouble Code Descriptions.
		try:
			with open(VehicleFile) as ThisFile:
				for ThisLine in ThisFile:
					Code, Description = ThisLine.partition(" ")[::2]
					self.TroubleCodeDescriptions[Code] = Description.strip()
		except Exception as Catch:
			print(STRING_ERROR + " " + VehicleFile + " : " + str(Catch))
			self.InitResult += "FAILED TO READ FILE: " + VehicleFile + "\n"



#/***********************************************/
#/* Close the serial port to the ELM327 device. */
#/***********************************************/
	def Close(self):
		Result = True

		# Close serial port.
		try:
			self.ELM327.close()
		except:
			Result = False



#/**************************************************/
#/* Perform a simple communication with the ELM327 */
#/* device to see if it is present and responding. */
#/**************************************************/
	def IsELM327Present(self):
		Result = False

		try:
			if self.GetResponse(b'AT @1\r') != "":
				Result = True
		except:
			Result = False

		return Result



#/******************************/
#/* Get the MIL on flag state. */
#/******************************/
	def GetMilOn(self):
		return self.MilOn



#/*******************************/
#/* Get the freeze frame count. */
#/*******************************/
	def GetFreezeFrameCount(self):
		return self.FreezeFrameCount



#/*************************************************/
#/* Get any errors or warnings which occured      */
#/* during creation of an instance of this class. */
#/*************************************************/
	def GetInitResult(self):
		return self.InitResult



#/*******************************************/
#/* Get infomation about the ELM327 device. */
#/*******************************************/
	def GetInfo(self):
		Result = ""

		try:
			# Get the current serial port in use by the ELM327 device.
			Result += "Serial Port|" + self.ELM327.name + "\n"
			# Get the ELM device version.
			Response = self.GetResponse(b'AT I\r')
			Result += "ELM Device Version|" + Response
			# Get the ELM device description.
			Response = self.GetResponse(b'AT @1\r')
			Result += "ELM Device Description|" + Response
			# Get the ELM device user supplied description.
			Response = self.GetResponse(b'AT @2\r')
			Result += "ELM Device User Data|" + Response
			# Get the current OBDII data protocol after OBDII CAN BUS communication.
			Response = self.GetResponse(b'AT DP\r')
			Result += "Using CAN BUS Protocol|" + Response
			# Get the Voltage measured at the OBDII connector.
			Response = self.GetResponse(b'AT RV\r')
			Result += "Volt At OBDII Connector|" + Response
			# Get the CAN status.
			Response = self.GetResponse(b'AT CS\r')
			Result += "CAN Status|" + Response
			# Get the key words.
			Response = self.GetResponse(b'AT KW\r')
			Result += "Key Words|" + Response
			# Get the ELM327 buffer dump.
			Response = self.GetResponse(b'AT BD\r')
			Result += "ELM327 Buffer Dump|" + Response
			# Get the programmable paramaters.
			Response = self.GetResponse(b'AT PPS\r')
			Result += "ELM327 Programmable Paramaters:|\n" + Response
		except:
			Result += "\nWARNING: PARTIAL DATA RETURNED\nTHIS COULD BE A FAKE ELM327 DEVICE AND SHOULD NOT BE USED IF IT IS FAKE.\n"

		return Result



#/********************************************************/
#/* Connect the ELM327 device to the CAN BUS on the ECU. */
#/* Then get a list of all of the valid PID addresses    */
#/* the ECU supports.                                    */
#/********************************************************/
	def Connect(self):
		Result = CONNECT_SUCCESS
		self.InitResult = ""

#  /****************************************************************/
# /* Open the required serial port which the ELM327 device is on. */
#/****************************************************************/
		try:
			self.ELM327 = serial.Serial(SERIAL_PORT_NAME, SERIAL_PORT_BAUD)
			self.ELM327.timeout = SERIAL_PORT_TIME_OUT
			self.ELM327.write_timeout = SERIAL_PORT_TIME_OUT

			time.sleep(ELM_RESET_PERIOD)

			# Initialize the ELM327 device.
			Response = self.GetResponse(b'AT Z\r')

			time.sleep(ELM_RESET_PERIOD)

			# Echo Off, for faster communications.
			Response = self.GetResponse(b'AT E0\r').replace('\r', '')
			if Response != 'AT E0\nOK\n':
				self.InitResult += "FAILED: AT E0 (Set Echo Off)\n"

			# Linefeed off, for faster communications.
			if self.InitResult == "":
				Response = self.GetResponse(b'AT L0\r').replace('\r', '')
				if Response != 'OK\n':
					self.InitResult += "FAILED: AT L0 (Set Linefeed Off)\n"

			# Responses on, for format recognition.
			if self.InitResult == "":
				Response = self.GetResponse(b'AT R1\r')
				if Response != 'OK\n':
					self.InitResult += "FAILED: AT R1 (Set Responses On)\n"

			# Headers off, for format recognition.
			if self.InitResult == "":
				Response = self.GetResponse(b'AT H0\r')
				if Response != 'OK\n':
					self.InitResult += "FAILED: AT H0 (Set Headers Off)\n"

			# Don't print space characters, for faster communications.
			if self.InitResult == "":
				Response = self.GetResponse(b'AT S0\r')
				if Response != 'OK\n':
					self.InitResult += "FAILED: AT S0 (Set Space Characters Off)\n"

			# Set CAN communication protocol to ISO 9141-2 or auto detect on fail.
			if self.InitResult == "":
				Response = self.GetResponse(b'AT SP A3\r')
				if Response != 'OK\n':
					self.InitResult += "FAILED: AT SP A3 (Set Protocol ISO 9141-2 / Auto)\n"

			# Set CAN Baud to high speed.
			if self.InitResult == "":
				Response = self.GetResponse(b'AT IB 10\r')
				if Response[-3:] != 'OK\n':
					self.InitResult += "FAILED: AT IB 10 (Set High Speed CAN BUS)\n"

			if self.InitResult != "":
				Result = CONNECT_ELM327_FAIL
				self.InitResult += "FAILED TO INITIALIZE ELM327 DEVICE.\n"
		except Exception as Catch:
			Result = CONNECT_ELM327_FAIL
			self.InitResult += "FAILED TO INITIALIZE ELM327 DEVICE.\n"
			print(str(Catch))

		if Result == CONNECT_SUCCESS:
			# Wait before tring to connect to ensure EML device is idle.
			time.sleep(ELM_CONNECT_SETTLE_PERIOD)
			# Request Mode 01 PID 01 (MIL Information) to test connection.
			Response = self.GetResponse(b'0101\r')
			if Response.find("UNABLE TO CONNECT") != -1:
				Result = CONNECT_CAN_BUS_FAIL
				# Close serial port if connection failed.
				self.ELM327.close()
			else:
				Response = self.PruneData(Response, 2)
				ResultVal1 = int(Response[:2], 16)
				if (ResultVal1 & 0x80) != 0:
					self.MilOn = True
				self.FreezeFrameCount = ResultVal1 & 0x7F

		if Result == CONNECT_SUCCESS:
			# Manually add standard PIDs supported, prefix with '!', don't show as user selectable option.
			# Application specific display locations.
			self.ValidPIDs['03'] = "! Show stored Diagnostic Trouble Codes"
			self.ValidPIDs['04'] = "! Clear Diagnostic Trouble Codes and stored values"
			self.ValidPIDs['07'] = "! Show pending Diagnostic Trouble Codes (detected during current or last driving cycle)"

			# Get Mode 01 PID support [01 -> 20].
			self.PID0100()
			# If Mode 01 PID 20 is supported, get Mode 01 PID support [21 -> 40].
			if '0120' in self.ValidPIDs:
				self.PID0120()
			# If Mode 01 PID 40 is supported, get Mode 01 PID support [41 -> 60].
			if '0140' in self.ValidPIDs:
				self.PID0140()
			# If Mode 01 PID 60 is supported, get Mode 01 PID support [61 -> 80].
			if '0160' in self.ValidPIDs:
				self.PID0160()
			# If Mode 01 PID 80 is supported, get Mode 01 PID support [81 -> A0].
			if '0180' in self.ValidPIDs:
				self.PID0180()
			# If Mode 01 PID A0 is supported, get Mode 01 PID support [A1 -> C0].
			if '01A0' in self.ValidPIDs:
				self.PID01A0()
			# If Mode 01 PID C0 is supported, get Mode 01 PID support [C1 -> E0].
			if '01C0' in self.ValidPIDs:
				self.PID01C0()
			# Get Mode 05 PID support.
			self.PID050100()
			# Get Mode 09 PID support.
			self.PID0900()

		return Result



#/***************************************************************/
#/* Return a list of PIDs the currently connected ECU supports. */
#/***************************************************************/
	def GetValidPIDs(self, FreezeIndex = -1):
		Result = self.ValidPIDs

		if FreezeIndex != -1:
			# Get Mode 02 PID support [01 -> 20].
			self.PID0200(FreezeIndex)
			# If Mode 02 PID 20 is supported, get Mode 02 PID support [21 -> 40].
			if '0120' in self.ValidFreezePIDs:
				self.PID0220(FreezeIndex)
			# If Mode 02 PID 40 is supported, get Mode 02 PID support [41 -> 60].
			if '0140' in self.ValidFreezePIDs:
				self.PID0240(FreezeIndex)
			# If Mode 02 PID 60 is supported, get Mode 02 PID support [61 -> 80].
			if '0160' in self.ValidFreezePIDs:
				self.PID0260(FreezeIndex)
			# If Mode 02 PID 80 is supported, get Mode 02 PID support [81 -> A0].
			if '0180' in self.ValidFreezePIDs:
				self.PID0280(FreezeIndex)
			# If Mode 02 PID A0 is supported, get Mode 02 PID support [A1 -> C0].
			if '01A0' in self.ValidFreezePIDs:
				self.PID02A0(FreezeIndex)
			# If Mode 02 PID C0 is supported, get Mode 02 PID support [C1 -> E0].
			if '01C0' in self.ValidFreezePIDs:
				self.PID02C0(FreezeIndex)
			Result = self.ValidFreezePIDs

		return Result



#/**********************************************************************/
#/* Get and return the information for the specified PID from the ECU. */
#/**********************************************************************/
	def DoPID(self, PID, FreezeIndex = -1):
		try:
			if PID in PidFunctions:
				Result = PidFunctions[PID](self, FreezeIndex)
			else:
				Result = STRING_NOT_IMPLEMENTED
		except Exception as Catch:
			print(STRING_ERROR + " in PID" + str(PID) + " : " + str(Catch))
			Result = STRING_ERROR

		return Result



#/*************************************************/
#/* Talk to the ELM327 device over a serial port. */
#/* Send request data, and wait for the response. */
#/* The expected response ends with a prompt      */
#/* character '>', the ELM327 provides promting   */
#/* for more user requests.                       */
#/* Otherwise a timeout occurs waiting for a      */
#/* response.                                     */
#/*************************************************/
	def GetResponse(self, Data):
		Data = Data.replace(b'\r', SERIAL_LINEFEED_TYPE)

		if DEBUG == "ON":
			print("DEBUG SENDING [" + str(len(Data)) + "] " + str(Data))

		self.ELM327.write(Data)
		Response = ""
		ReadChar = 1
		while ReadChar != b'>' and ReadChar != b'' and ReadChar != 0:
			ReadChar = self.ELM327.read()
			if ReadChar[0] > 127:
				if DEBUG == "ON":
					print("REJECTING RECEIVED CHARACTER: " + str(int(ReadChar[0])))
			elif ReadChar != b'>':
				Response += str(ReadChar, 'utf-8')
		Result = Response.replace('\r', '\n').replace('\n\n', '\n').replace('NO DATA', '00000000000000')
		if Result[-1:] != '\n':
			Result += '\n'

		if DEBUG == "ON":
			print("DEBUG RECEIVED [" + str(len(Result)) + "] " + str(Result))

		return Result



#/*****************************************************************/
#/* Resolve a bitmaped supported PIDs response from the ECU and   */
#/* add them to the list of currently supported PIDs for the ECU. */
#/*****************************************************************/
	def ResolvePidData(self, PidMode, PidData, PidStart, PidDescriptions, FreezeIndex = -1):
		PidStartValue = int(PidStart, 16)
		PidValue = int(PidData, 16)
		Count = PidStartValue + (len(PidData) * 4)
		while PidValue > 0:
			if PidValue % 2 > 0:
				PidIndex = '%2.2X' % Count
				if PidMode == '02':
					ThisFreezeIndex = "{:02d}".format(FreezeIndex)
					if PidIndex in PidDescriptions:
						self.ValidFreezePIDs[PidMode + PidIndex + ThisFreezeIndex] = PidDescriptions[PidIndex]
					else:
						self.ValidFreezePIDs[PidMode + PidIndex + ThisFreezeIndex] = STRING_NO_DESCRIPTION
				else:
					if PidIndex in PidDescriptions:
						self.ValidPIDs[PidMode + PidIndex] = PidDescriptions[PidIndex]
					else:
						self.ValidPIDs[PidMode + PidIndex] = STRING_NO_DESCRIPTION
			PidValue = int(PidValue / 2)
			Count -= 1



#/**********************************************************/
#/* Convert pairs of data bytes into actual trouble codes, */
#/* translating the first digit as required, and ignoring  */
#/* zero value data.                                       */
#/**********************************************************/
	def DataToTroubleCodes(self, Data):
		TroubleCodes = list()
		while len(Data) > 0:
			ThisCode = Data[:4]
			if int(ThisCode) != 0:
				TroubleCodes.append(self.TroubleCodePrefix[ThisCode[0]] + ThisCode[1:])
			Data = Data[4:]
		return TroubleCodes



#/*****************************************************/
#/* Get the trouble codes from the ECU and lookup the */
#/* trouble code descriptions. Return the data in a   */
#/* data array.                                       */
#/*****************************************************/
	def GetTroubleCodeData(self, OBDIImode):
		TroubleCodeData = {}
		Response = self.GetResponse(OBDIImode + b'\r')
		Response = self.PruneData(Response, 1)
		TroubleCodes = self.DataToTroubleCodes(Response)
		for TroubleCode in TroubleCodes:
			if TroubleCode in self.TroubleCodeDescriptions:
				TroubleCodeData[TroubleCode] = self.TroubleCodeDescriptions[TroubleCode]
			else:
				TroubleCodeData[TroubleCode] = STRING_NO_DESCRIPTION
		return TroubleCodeData



#/*******************************************************/
#/* The OBDII protocol will sometimes prefix a response */
#/* with confirmation of the request sent or other      */
#/* unwanted bytes of data. Use this function to remove */
#/* unwanted bytes from the start of lines, and         */
#/* concatenate the remainder of the response into a    */
#/* single line of data, ready for processing.          */
#/*******************************************************/
	def PruneData(self, Data, RemoveByteCount):
		Response = ""
		for Line in Data.split('\n'):
			Response += Line[2 * RemoveByteCount:]
		return Response


#/**************************************/
#/* ODBII MODE 01 - Show current data. */
#/**************************************/

# PID0100 Supported PIDs for Mode 1 [01 -> 20].
	def PID0100(self, FreezeIndex = -1):
		Response = self.GetResponse(b'0100\r')
		Response = self.PruneData(Response, 2)
		self.ResolvePidData('01', Response, '00', self.PidDescriptionsMode01)
	PidFunctions["0100"] = PID0100


# PID0101 Get Monitor status since DTCs cleared from the ECU.
	def PID0101(self, FreezeIndex = -1):
		Result = STRING_NO_DATA
		ResultArray = ()

		if '0101' in self.ValidPIDs:
			if FreezeIndex == -1:
				Response = self.GetResponse(b'0101\r')
				Response = self.PruneData(Response, 2)
			else:
				Response = self.GetResponse(bytearray("0201" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
				Response = self.PruneData(Response, 3)

			ResultVal1 = int(Response[:2], 16)
			if (ResultVal1 & 0x80) != 0:
				self.MilOn = True
				ResultArray += ("MIL:ON",)
			else:
				self.MilOn = False
				ResultArray += ("MIL:OFF",)
			self.FreezeFrameCount = ResultVal1 & 0x7F
			ResultArray += ("STORED TROUBLE CODE COUNT|" + str(self.FreezeFrameCount),)

			ResultVal1 = int(Response[2:4], 16)

			AppendText = ""
			if (ResultVal1 & 0x01) != 0:
				AppendText = "MISSFIRE TEST"
				if (ResultVal1 & 0x10) != 0:
					AppendText += "|[INCOMPLETE]"
			ResultArray += (AppendText,)

			AppendText = ""
			if (ResultVal1 & 0x02) != 0:
				AppendText = "FUEL SYSTEM TEST"
				if (ResultVal1 & 0x20) != 0:
					AppendText += "|[INCOMPLETE]"
			ResultArray += (AppendText,)

			AppendText = ""
			if (ResultVal1 & 0x04) != 0:
				AppendText = "COMPONENTS TEST"
				if (ResultVal1 & 0x40) != 0:
					AppendText += "|[INCOMPLETE]"
			ResultArray += (AppendText,)

			if (ResultVal1 & 0x08) != 0:
				ResultArray += ("IGNITION|COMPRESSION",)

				ResultVal1 = int(Response[4:6], 16)
				ResultVal2 = int(Response[6:8], 16)

				AppendText = ""
				if (ResultVal1 & 0x01) != 0:
					AppendText = "NMHC CATALYST TEST"
					if (ResultVal2 & 0x01) != 0:
						AppendText += "|[INCOMPLETE]"
				ResultArray += (AppendText,)

				AppendText = ""
				if (ResultVal1 & 0x02) != 0:
					AppendText = "NOx/SCR MONITOR TEST"
					if (ResultVal2 & 0x02) != 0:
						AppendText += "|[INCOMPLETE]"
				ResultArray += (AppendText,)

				AppendText = ""
				if (ResultVal1 & 0x04) != 0:
					AppendText = "Reserved 1 TEST"
					if (ResultVal2 & 0x04) != 0:
						AppendText += "|[INCOMPLETE]"
				ResultArray += (AppendText,)

				AppendText = ""
				if (ResultVal1 & 0x08) != 0:
					AppendText = "BOOST PRESSURE TEST"
					if (ResultVal2 & 0x08) != 0:
						AppendText += "|[INCOMPLETE]"
				ResultArray += (AppendText,)

				AppendText = ""
				if (ResultVal1 & 0x10) != 0:
					AppendText = "Reserved 2 TEST"
					if (ResultVal2 & 0x10) != 0:
						AppendText += "|[INCOMPLETE]"
				ResultArray += (AppendText,)

				AppendText = ""
				if (ResultVal1 & 0x20) != 0:
					AppendText = "EXHAUST GAS SENSOR TEST"
					if (ResultVal2 & 0x20) != 0:
						AppendText += "|[INCOMPLETE]"
				ResultArray += (AppendText,)

				AppendText = ""
				if (ResultVal1 & 0x40) != 0:
					AppendText = "PM FILTER MONITORING TEST"
					if (ResultVal2 & 0x40) != 0:
						AppendText += "|[INCOMPLETE]"
				ResultArray += (AppendText,)

				AppendText = ""
				if (ResultVal1 & 0x80) != 0:
					AppendText = "EGR/VVT SYSTEM TEST"
					if (ResultVal2 & 0x80) != 0:
						AppendText += "|[INCOMPLETE]"
				ResultArray += (AppendText,)
			else:
				ResultArray += ("IGNITION|SPARK",)

				ResultVal1 = int(Response[4:6], 16)
				ResultVal2 = int(Response[6:8], 16)

				AppendText = ""
				if (ResultVal1 & 0x01) != 0:
					AppendText = "CATALYST TEST"
					if (ResultVal2 & 0x01) != 0:
						AppendText += "|[INCOMPLETE]"
				ResultArray += (AppendText,)

				AppendText = ""
				if (ResultVal1 & 0x02) != 0:
					AppendText = "HEATED CATALYST TEST"
					if (ResultVal2 & 0x02) != 0:
						AppendText += "|[INCOMPLETE]"
				ResultArray += (AppendText,)

				AppendText = ""
				if (ResultVal1 & 0x04) != 0:
					AppendText = "EVAPORATIVE SYSTEM TEST"
					if (ResultVal2 & 0x04) != 0:
						AppendText += "|[INCOMPLETE]"
				ResultArray += (AppendText,)

				AppendText = ""
				if (ResultVal1 & 0x08) != 0:
					AppendText = "SECONDARY AIR SYSTEM TEST"
					if (ResultVal2 & 0x08) != 0:
						AppendText += "|[INCOMPLETE]"
				ResultArray += (AppendText,)

				AppendText = ""
				if (ResultVal1 & 0x10) != 0:
					AppendText = "A/C REFRIGERANT TEST"
					if (ResultVal2 & 0x10) != 0:
						AppendText += "|[INCOMPLETE]"
				ResultArray += (AppendText,)

				AppendText = ""
				if (ResultVal1 & 0x20) != 0:
					AppendText = "OXYGEN SENSOR TEST"
					if (ResultVal2 & 0x20) != 0:
						AppendText += "|[INCOMPLETE]"
				ResultArray += (AppendText,)

				AppendText = ""
				if (ResultVal1 & 0x40) != 0:
					AppendText = "OXYGEN SENSOR HEATER TEST"
					if (ResultVal2 & 0x40) != 0:
						AppendText += "|[INCOMPLETE]"
				ResultArray += (AppendText,)

				AppendText = ""
				if (ResultVal1 & 0x80) != 0:
					AppendText = "EGR SYSTEM TEST"
					if (ResultVal2 & 0x80) != 0:
						AppendText += "|[INCOMPLETE]"
				ResultArray += (AppendText,)

			Result = ResultArray

		return Result
	PidFunctions["0101"] = PID0101
	PidFunctions["0201"] = PID0101


# PID0102 Freeze DTC.
	def PID0102(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if FreezeIndex == -1:
			Response = self.GetResponse(b'0102\r')
			Response = self.PruneData(Response, 2)
		else:
			Response = self.GetResponse(bytearray("0202" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
			Response = self.PruneData(Response, 3)

		TroubleCodes = self.DataToTroubleCodes(Response)
		if TroubleCodes[0] in self.TroubleCodeDescriptions:
			Result = TroubleCodes[0] + " " + self.TroubleCodeDescriptions[TroubleCodes[0]]
		else:
			Result = STRING_NO_DESCRIPTION

		return Result
	PidFunctions["0102"] = PID0102
	PidFunctions["0202"] = PID0102


# PID0103 Get the Fuel system status from the ECU.
	def PID0103(self, FreezeIndex = -1):
		Result = STRING_NO_DATA
		ResultArray = ()

		if '0103' in self.ValidPIDs:
			if FreezeIndex == -1:
				Response = self.GetResponse(b'0103\r')
				Response = self.PruneData(Response, 2)
			else:
				Response = self.GetResponse(bytearray("0203" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
				Response = self.PruneData(Response, 3)
			if Response[:2] in self.FuelSystemStatus:
				ResultArray += ("Fuel System 1",)
				ResultArray += (self.FuelSystemStatus[Response[:2]],)
			else:
				ResultArray += ("Fuel System 1",)
				ResultArray += (STRING_INVALID,)
			if Response[2:4] in self.FuelSystemStatus:
				ResultArray += ("Fuel System 2",)
				ResultArray += (self.FuelSystemStatus[Response[2:4]],)
			else:
				ResultArray += ("Fuel System 2",)
				ResultArray += (STRING_INVALID,)

			Result = ResultArray

		return Result
	PidFunctions["0103"] = PID0103
	PidFunctions["0203"] = PID0103


# PID0104 Get the current Calculated Engine Load from the ECU.
	def PID0104(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '0104' in self.ValidPIDs:
			if FreezeIndex == -1:
				Response = self.GetResponse(b'0104\r')
				Response = self.PruneData(Response, 2)
			else:
				Response = self.GetResponse(bytearray("0204" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
				Response = self.PruneData(Response, 3)
			Result = 100 * int(Response, 16) / 255

		return Result
	PidFunctions["0104"] = PID0104
	PidFunctions["0204"] = PID0104



# PID0105 Get the current Engine Coolant Temperature from the ECU.
	def PID0105(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '0105' in self.ValidPIDs:
			if FreezeIndex == -1:
				Response = self.GetResponse(b'0105\r')
				Response = self.PruneData(Response, 2)
			else:
				Response = self.GetResponse(bytearray("0205" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
				Response = self.PruneData(Response, 3)
			Result = int(Response, 16) - 40

		return Result
	PidFunctions["0105"] = PID0105
	PidFunctions["0205"] = PID0105


# PID0106 Get the current Short Term Fuel Trim Bank1 from the ECU.
	def PID0106(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '0106' in self.ValidPIDs:
			if FreezeIndex == -1:
				Response = self.GetResponse(b'0106\r')
				Response = self.PruneData(Response, 2)
			else:
				Response = self.GetResponse(bytearray("0206" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
				Response = self.PruneData(Response, 3)
			Result = (100 * int(Response, 16) / 128) - 100

		return Result
	PidFunctions["0106"] = PID0106
	PidFunctions["0206"] = PID0106


# PID0107 Get the Long term fuel trim—Bank from the ECU.
	def PID0107(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '0107' in self.ValidPIDs:
			if FreezeIndex == -1:
				Response = self.GetResponse(b'0107\r')
				Response = self.PruneData(Response, 2)
			else:
				Response = self.GetResponse(bytearray("0207" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
				Response = self.PruneData(Response, 3)
			Result = (100 * int(Response, 16) / 128) - 100

		return Result
	PidFunctions["0107"] = PID0107
	PidFunctions["0207"] = PID0107


# PID0108 Get the Short term fuel trim—Bank 2 from the ECU.
	def PID0108(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '0108' in self.ValidPIDs:
			if FreezeIndex == -1:
				Response = self.GetResponse(b'0108\r')
				Response = self.PruneData(Response, 2)
			else:
				Response = self.GetResponse(bytearray("0208" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
				Response = self.PruneData(Response, 3)
			Result = (100 * int(Response, 16) / 128) - 100

		return Result
	PidFunctions["0108"] = PID0108
	PidFunctions["0208"] = PID0108


# PID0109 Get the Long term fuel trim—Bank 2 from the ECU.
	def PID0109(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '0109' in self.ValidPIDs:
			if FreezeIndex == -1:
				Response = self.GetResponse(b'0109\r')
				Response = self.PruneData(Response, 2)
			else:
				Response = self.GetResponse(bytearray("0209" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
				Response = self.PruneData(Response, 3)
			Result = (100 * int(Response, 16) / 128) - 100

		return Result
	PidFunctions["0109"] = PID0109
	PidFunctions["0209"] = PID0109


# PID010A Get the Fuel pressure (gauge pressure) from the ECU.
	def PID010A(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '010A' in self.ValidPIDs:
			if FreezeIndex == -1:
				Response = self.GetResponse(b'010A\r')
				Response = self.PruneData(Response, 2)
			else:
				Response = self.GetResponse(bytearray("020A" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
				Response = self.PruneData(Response, 3)
			Result = 3 * int(Response, 16)

		return Result
	PidFunctions["010A"] = PID010A
	PidFunctions["020A"] = PID010A


# PID010B Get the Intake manifold absolute pressure from the ECU.
	def PID010B(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '010B' in self.ValidPIDs:
			if FreezeIndex == -1:
				Response = self.GetResponse(b'010B\r')
				Response = self.PruneData(Response, 2)
			else:
				Response = self.GetResponse(bytearray("020B" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
				Response = self.PruneData(Response, 3)
			Result = int(Response, 16)

		return Result
	PidFunctions["010B"] = PID010B
	PidFunctions["020B"] = PID010B


# PID010C Get the current Engine RPM from the ECU.
	def PID010C(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '010C' in self.ValidPIDs:
			if FreezeIndex == -1:
				Response = self.GetResponse(b'010C\r')
				Response = self.PruneData(Response, 2)
			else:
				Response = self.GetResponse(bytearray("020C" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
				Response = self.PruneData(Response, 3)
			Result = (256 * int(Response[:2], 16) + int(Response[2:4], 16)) / 4

		return Result
	PidFunctions["010C"] = PID010C
	PidFunctions["020C"] = PID010C


# PID010D Get the Vehicle speed from the ECU.
	def PID010D(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '010D' in self.ValidPIDs:
			if FreezeIndex == -1:
				Response = self.GetResponse(b'010D\r')
				Response = self.PruneData(Response, 2)
			else:
				Response = self.GetResponse(bytearray("020D" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
				Response = self.PruneData(Response, 3)
			Result = int(Response[:2], 16)

		return Result
	PidFunctions["010D"] = PID010D
	PidFunctions["020D"] = PID010D


# PID010E Get the Timing advance from the ECU.
	def PID010E(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '010E' in self.ValidPIDs:
			if FreezeIndex == -1:
				Response = self.GetResponse(b'010E\r')
				Response = self.PruneData(Response, 2)
			else:
				Response = self.GetResponse(bytearray("020E" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
				Response = self.PruneData(Response, 3)
			Result = (int(Response[:2], 16) / 2) - 64

		return Result
	PidFunctions["010E"] = PID010E
	PidFunctions["020E"] = PID010E


# PID010F Get the Intake air temperature from the ECU.
	def PID010F(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '010F' in self.ValidPIDs:
			if FreezeIndex == -1:
				Response = self.GetResponse(b'010F\r')
				Response = self.PruneData(Response, 2)
			else:
				Response = self.GetResponse(bytearray("020F" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
				Response = self.PruneData(Response, 3)
			Result = int(Response[:2], 16) - 40

		return Result
	PidFunctions["010F"] = PID010F
	PidFunctions["020F"] = PID010F


# PID0110 Get the MAF air flow rate from the ECU.
	def PID0110(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '0110' in self.ValidPIDs:
			if FreezeIndex == -1:
				Response = self.GetResponse(b'0110\r')
				Response = self.PruneData(Response, 2)
			else:
				Response = self.GetResponse(bytearray("0210" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
				Response = self.PruneData(Response, 3)
			Result = (256 * int(Response[:2], 16) + int(Response[2:4], 16)) / 100

		return Result
	PidFunctions["0110"] = PID0110
	PidFunctions["0210"] = PID0110


# PID0111 Get the Throttle position from the ECU.
	def PID0111(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '0111' in self.ValidPIDs:
			if FreezeIndex == -1:
				Response = self.GetResponse(b'0111\r')
				Response = self.PruneData(Response, 2)
			else:
				Response = self.GetResponse(bytearray("0211" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
				Response = self.PruneData(Response, 3)
			Result = 100 * int(Response[:2], 16) / 255

		return Result
	PidFunctions["0111"] = PID0111
	PidFunctions["0211"] = PID0111


# PID0112 Get the Commanded secondary air status from the ECU.
	def PID0112(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '0112' in self.ValidPIDs:
			if FreezeIndex == -1:
				Response = self.GetResponse(b'0112\r')
				Response = self.PruneData(Response, 2)
			else:
				Response = self.GetResponse(bytearray("0212" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
				Response = self.PruneData(Response, 3)
			if Response in self.CommandedSecondaryAirStatus:
				Result = self.CommandedSecondaryAirStatus[Response]
			else:
				Result = STRING_INVALID

		return Result
	PidFunctions["0112"] = PID0112
	PidFunctions["0212"] = PID0112


# PID0113 Get the Oxygen sensors present (in 2 banks) from the ECU.
	def PID0113(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '0113' in self.ValidPIDs:
			if FreezeIndex == -1:
				Response = self.GetResponse(b'0113\r')
				Response = self.PruneData(Response, 2)
			else:
				Response = self.GetResponse(bytearray("0213" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
				Response = self.PruneData(Response, 3)
			ResultVal = int(Response[:2], 16)
			Result = ( "BANK1", (ResultVal & 0x0F), "BANK2", (ResultVal & 0xF0) >> 4)

		return Result
	PidFunctions["0113"] = PID0113
	PidFunctions["0213"] = PID0113


# PID0114 Get the current Oxygen Sensor 1 Voltage & Short Term Fuel Trim from the ECU.
	def PID0114(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '0114' in self.ValidPIDs:
			if FreezeIndex == -1:
				Response = self.GetResponse(b'0114\r')
				Response = self.PruneData(Response, 2)
			else:
				Response = self.GetResponse(bytearray("0214" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
				Response = self.PruneData(Response, 3)
			Result = ( int(Response[:2], 16) / 200, (100 * int(Response[2:4], 16) / 128) - 100 )

		return Result
	PidFunctions["0114"] = PID0114
	PidFunctions["0214"] = PID0114


# PID0115 Get the current Oxygen Sensor 2 Voltage & Short Term Fuel Trim from the ECU.
	def PID0115(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '0115' in self.ValidPIDs:
			if FreezeIndex == -1:
				Response = self.GetResponse(b'0115\r')
				Response = self.PruneData(Response, 2)
			else:
				Response = self.GetResponse(bytearray("0215" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
				Response = self.PruneData(Response, 3)
			Result = ( int(Response[:2], 16) / 200, (100 * int(Response[2:4], 16) / 128) - 100 )

		return Result
	PidFunctions["0115"] = PID0115
	PidFunctions["0215"] = PID0115


# PID0116 Get the current Oxygen Sensor 3 Voltage & Short Term Fuel Trim from the ECU.
	def PID0116(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '0116' in self.ValidPIDs:
			if FreezeIndex == -1:
				Response = self.GetResponse(b'0116\r')
				Response = self.PruneData(Response, 2)
			else:
				Response = self.GetResponse(bytearray("0216" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
				Response = self.PruneData(Response, 3)
			Result = ( int(Response[:2], 16) / 200, (100 * int(Response[2:4], 16) / 128) - 100 )

		return Result
	PidFunctions["0116"] = PID0116
	PidFunctions["0216"] = PID0116


# PID0117 Get the current Oxygen Sensor 4 Voltage & Short Term Fuel Trim from the ECU.
	def PID0117(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '0117' in self.ValidPIDs:
			if FreezeIndex == -1:
				Response = self.GetResponse(b'0117\r')
				Response = self.PruneData(Response, 2)
			else:
				Response = self.GetResponse(bytearray("0217" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
				Response = self.PruneData(Response, 3)
			Result = ( int(Response[:2], 16) / 200, (100 * int(Response[2:4], 16) / 128) - 100 )

		return Result
	PidFunctions["0117"] = PID0117
	PidFunctions["0217"] = PID0117


# PID0118 Get the current Oxygen Sensor 5 Voltage & Short Term Fuel Trim from the ECU.
	def PID0118(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '0118' in self.ValidPIDs:
			if FreezeIndex == -1:
				Response = self.GetResponse(b'0118\r')
				Response = self.PruneData(Response, 2)
			else:
				Response = self.GetResponse(bytearray("0218" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
				Response = self.PruneData(Response, 3)
			Result = ( int(Response[:2], 16) / 200, (100 * int(Response[2:4], 16) / 128) - 100 )

		return Result
	PidFunctions["0118"] = PID0118
	PidFunctions["0218"] = PID0118


# PID0119 Get the current Oxygen Sensor 6 Voltage & Short Term Fuel Trim from the ECU.
	def PID0119(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '0119' in self.ValidPIDs:
			if FreezeIndex == -1:
				Response = self.GetResponse(b'0119\r')
				Response = self.PruneData(Response, 2)
			else:
				Response = self.GetResponse(bytearray("0219" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
				Response = self.PruneData(Response, 3)
			Result = ( int(Response[:2], 16) / 200, (100 * int(Response[2:4], 16) / 128) - 100 )

		return Result
	PidFunctions["0119"] = PID0119
	PidFunctions["0219"] = PID0119


# PID011A Get the current Oxygen Sensor 7 Voltage & Short Term Fuel Trim from the ECU.
	def PID011A(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '011A' in self.ValidPIDs:
			if FreezeIndex == -1:
				Response = self.GetResponse(b'011A\r')
				Response = self.PruneData(Response, 2)
			else:
				Response = self.GetResponse(bytearray("021A" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
				Response = self.PruneData(Response, 3)
			Result = ( int(Response[:2], 16) / 200, (100 * int(Response[2:4], 16) / 128) - 100 )

		return Result
	PidFunctions["011A"] = PID011A
	PidFunctions["021A"] = PID011A


# PID011B Get the current Oxygen Sensor 8 Voltage & Short Term Fuel Trim from the ECU.
	def PID011B(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '011B' in self.ValidPIDs:
			if FreezeIndex == -1:
				Response = self.GetResponse(b'011B\r')
				Response = self.PruneData(Response, 2)
			else:
				Response = self.GetResponse(bytearray("021B" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
				Response = self.PruneData(Response, 3)
			Result = ( int(Response[:2], 16) / 200, (100 * int(Response[2:4], 16) / 128) - 100 )

		return Result
	PidFunctions["011B"] = PID011B
	PidFunctions["021B"] = PID011B


# PID011C Get the OBD standards this vehicle conforms to from the ECU.
	def PID011C(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '011C' in self.ValidPIDs:
			if FreezeIndex == -1:
				Response = self.GetResponse(b'011C\r')
				Response = self.PruneData(Response, 2)
			else:
				Response = self.GetResponse(bytearray("021C" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
				Response = self.PruneData(Response, 3)
			if Response in self.VehicleObdStandards:
				Result = self.VehicleObdStandards[Response]
			else:
				Result = STRING_INVALID

		return Result
	PidFunctions["011C"] = PID011C
	PidFunctions["021C"] = PID011C


# PID011D
# PID011E
# PID011F


# PID0120 Supported PIDs for Mode 1 [21 -> 40].
	def PID0120(self, FreezeIndex = -1):
		Response = self.GetResponse(b'0120\r')
		Response = self.PruneData(Response, 2)
		self.ResolvePidData('01', Response, '20', self.PidDescriptionsMode01)
	PidFunctions["0120"] = PID0120


# PID0121 Get the Distance traveled with malfunction indicator lamp (MIL) on from the ECU.
	def PID0121(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '0121' in self.ValidPIDs:
			if FreezeIndex == -1:
				Response = self.GetResponse(b'0121\r')
				Response = self.PruneData(Response, 2)
			else:
				Response = self.GetResponse(bytearray("0221" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
				Response = self.PruneData(Response, 3)
			Result = 256 * int(Response[:2], 16) + int(Response[2:4], 16)

		return Result
	PidFunctions["0121"] = PID0121
	PidFunctions["0221"] = PID0121


# PID0122
# PID0123
# PID0124
# PID0125
# PID0126
# PID0127
# PID0128
# PID0129
# PID012A
# PID012B
# PID012C
# PID012D
# PID012E
# PID012F
# PID0130
# PID0131
# PID0132
# PID0133
# PID0134
# PID0135
# PID0136
# PID0137
# PID0138
# PID0139
# PID013A
# PID013B
# PID013C
# PID013D
# PID013E
# PID013F


# PID0140 Supported PIDs for Mode 1 [41 -> 60].
	def PID0140(self, FreezeIndex = -1):
		Response = self.GetResponse(b'0140\r')
		Response = self.PruneData(Response, 2)
		self.ResolvePidData('01', Response, '40', self.PidDescriptionsMode01)
	PidFunctions["0140"] = PID0140


# PID0141
# PID0142
# PID0143
# PID0144
# PID0145
# PID0146
# PID0147
# PID0148
# PID0149
# PID014A
# PID014B
# PID014C
# PID014D
# PID014E
# PID014F
# PID0150
# PID0151
# PID0152
# PID0153
# PID0154
# PID0155
# PID0156
# PID0157
# PID0158
# PID0159
# PID015A
# PID015B
# PID015C
# PID015D
# PID015E
# PID015F


# PID0160 Supported PIDs for Mode 1 [61 -> 80].
	def PID0160(self, FreezeIndex = -1):
		Response = self.GetResponse(b'0160\r')
		Response = self.PruneData(Response, 2)
		self.ResolvePidData('01', Response, '60', self.PidDescriptionsMode01)
	PidFunctions["0160"] = PID0160


# PID0161
# PID0162
# PID0163
# PID0164
# PID0165
# PID0166
# PID0167
# PID0168
# PID0169
# PID016A
# PID016B
# PID016C
# PID016D
# PID016E
# PID016F
# PID0170
# PID0171
# PID0172
# PID0173
# PID0174
# PID0175
# PID0176
# PID0177
# PID0178
# PID0179
# PID017A
# PID017B
# PID017C
# PID017D
# PID017E
# PID017F


# PID0180 Supported PIDs for Mode 1 [81 -> A0].
	def PID0180(self, FreezeIndex = -1):
		Response = self.GetResponse(b'0180\r')
		Response = self.PruneData(Response, 2)
		self.ResolvePidData('01', Response, '80', self.PidDescriptionsMode01)
	PidFunctions["0180"] = PID0180


# PID0181
# PID0182
# PID0183
# PID0184
# PID0185
# PID0186
# PID0187
# PID0188
# PID0189
# PID018A
# PID018B
# PID018C
# PID018D
# PID018E
# PID018F
# PID0190
# PID0191
# PID0192
# PID0193
# PID0194
# PID0195
# PID0196
# PID0197
# PID0198
# PID0199
# PID019A
# PID019B
# PID019C
# PID019D
# PID019E
# PID019F


# PID01A0 Supported PIDs for Mode 1 [A1 -> C0].
	def PID01A0(self, FreezeIndex = -1):
		Response = self.GetResponse(b'01A0\r')
		Response = self.PruneData(Response, 2)
		self.ResolvePidData('01', Response, 'A0', self.PidDescriptionsMode01)
	PidFunctions["01A0"] = PID01A0


# PID01A1
# PID01A2
# PID01A3
# PID01A4
# PID01A5
# PID01A6
# PID01A7
# PID01A8
# PID01A9
# PID01AA
# PID01AB
# PID01AC
# PID01AD
# PID01AE
# PID01AF
# PID01B0
# PID01B1
# PID01B2
# PID01B3
# PID01B4
# PID01B5
# PID01B6
# PID01B7
# PID01B8
# PID01B9
# PID01BA
# PID01BB
# PID01BC
# PID01BD
# PID01BE
# PID01BF


# PID01C0 Supported PIDs for Mode 1 [C1 -> E0].
	def PID01C0(self, FreezeIndex = -1):
		Response = self.GetResponse(b'01C0\r')
		Response = self.PruneData(Response, 2)
		self.ResolvePidData('01', Response, 'C0', self.PidDescriptionsMode01)
	PidFunctions["01C0"] = PID01C0


# PID01C1
# PID01C2
# PID01C3
# PID01C4
# PID01C5
# PID01C6
# PID01C7
# PID01C8
# PID01C9
# PID01CA
# PID01CB
# PID01CC
# PID01CD
# PID01CE
# PID01CF
# PID01D0
# PID01D1
# PID01D2
# PID01D3
# PID01D4
# PID01D5
# PID01D6
# PID01D7
# PID01D8
# PID01D9
# PID01DA
# PID01DB
# PID01DC
# PID01DD
# PID01DE
# PID01DF


#/*******************************************/
#/* ODBII MODE 02 - Show freeze frame data. */
#/*******************************************/

# PID0200 Supported PIDs for Mode 2 [01 -> 20].
	def PID0200(self, FreezeIndex = -1):
		Response = self.GetResponse(bytearray("0200" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
		Response = self.PruneData(Response, 3)
		self.ResolvePidData('02', Response, '00', self.PidDescriptionsMode01, FreezeIndex)
	PidFunctions["0200"] = PID0200


# PID0220 Supported PIDs for Mode 2 [21 -> 40].
	def PID0220(self, FreezeIndex = -1):
		Response = self.GetResponse(bytearray("0220" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
		Response = self.PruneData(Response, 3)
		self.ResolvePidData('02', Response, '20', self.PidDescriptionsMode01, FreezeIndex)
	PidFunctions["0220"] = PID0220


# PID0240 Supported PIDs for Mode 2 [41 -> 60].
	def PID0240(self, FreezeIndex = -1):
		Response = self.GetResponse(bytearray("0240" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
		Response = self.PruneData(Response, 3)
		self.ResolvePidData('02', Response, '40', self.PidDescriptionsMode01, FreezeIndex)
	PidFunctions["0240"] = PID0240


# PID0260 Supported PIDs for Mode 2 [61 -> 80].
	def PID0260(self, FreezeIndex = -1):
		Response = self.GetResponse(bytearray("0260" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
		Response = self.PruneData(Response, 3)
		self.ResolvePidData('02', Response, '60', self.PidDescriptionsMode01, FreezeIndex)
	PidFunctions["0260"] = PID0260


# PID0280 Supported PIDs for Mode 2 [81 -> A0].
	def PID0280(self, FreezeIndex = -1):
		Response = self.GetResponse(bytearray("0280" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
		Response = self.PruneData(Response, 3)
		self.ResolvePidData('02', Response, '80', self.PidDescriptionsMode01, FreezeIndex)
	PidFunctions["0280"] = PID0280


# PID02A0 Supported PIDs for Mode 2 [A1 -> C0].
	def PID02A0(self, FreezeIndex = -1):
		Response = self.GetResponse(bytearray("02A0" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
		Response = self.PruneData(Response, 3)
		self.ResolvePidData('02', Response, 'A0', self.PidDescriptionsMode01, FreezeIndex)
	PidFunctions["02A0"] = PID02A0


# PID02C0 Supported PIDs for Mode 2 [C1 -> E0].
	def PID02C0(self, FreezeIndex = -1):
		Response = self.GetResponse(bytearray("02C0" + "{:02d}".format(FreezeIndex) + "\r", 'UTF-8'))
		Response = self.PruneData(Response, 3)
		self.ResolvePidData('02', Response, 'C0', self.PidDescriptionsMode01)
	PidFunctions["02C0"] = PID02C0


#/*********************************************************/
#/* ODBII MODE 03 - Show stored diagnostic trouble codes. */
#/*********************************************************/

# PID03 Get the Stored Trouble Codes from the ECU.
	def PID03(self, FreezeIndex = -1):
		return self.GetTroubleCodeData(b'03')
	PidFunctions["03"] = PID03


#/*********************************************************************/
#/* ODBII MODE 04 - Clear diagnostic trouble codes and stored values. */
#/*********************************************************************/

# PID04 Erase all Pending/Stored Trouble Codes and Data from the ECU.
	def PID04(self, FreezeIndex = -1):
		return self.GetResponse(b'04\r')
	PidFunctions["04"] = PID04


#/**************************************************************************/
#/* ODBII MODE 05 - Test results, oxygen sensor monitoring (non CAN only). */
#/**************************************************************************/

# PID050100 Supported PIDs for Mode 0501 [01 -> 20].
	def PID050100(self, FreezeIndex = -1):
		Response = self.GetResponse(b'050100\r')
		Response = self.PruneData(Response, 3)
		self.ResolvePidData('05', Response, '00', self.PidDescriptionsMode05)
	PidFunctions["050100"] = PID050100


# PID050101
# PID050102
# PID050103
# PID050104
# PID050105
# PID050106
# PID050107
# PID050108
# PID050109
# PID05010A
# PID05010B
# PID05010C
# PID05010D
# PID05010E
# PID05010F
# PID050110
# PID050121
# PID050122
# PID050123
# PID050124
# PID050125
# PID050126
# PID050127
# PID050128
# PID050129
# PID05012A
# PID05012B
# PID05012C
# PID05012D
# PID05012E
# PID05012F


#/***********************************************************************/
#/* ODBII MODE 06 - Test results, other component/system monitoring.    */
#/*               (Test results, oxygen sensor monitoring for CAN only) */
#/***********************************************************************/


#/*******************************************************************/
#/* ODBII MODE 07 - Show pending diagnostic trouble codes.          */
#/*                 (detected during current or last driving cycle) */
#/*******************************************************************/

# Get the Pending Trouble Codes from the ECU.
	def PID07(self, FreezeIndex = -1):
		return self.GetTroubleCodeData(b'07')
	PidFunctions["07"] = PID07


#/*******************************************************************/
#/* ODBII MODE 08 - Control operation of on-board component/system. */
#/*******************************************************************/


#/************************************************/
#/* ODBII MODE 09 - Request vehicle information. */
#/************************************************/

# PID0900 Supported PIDs for Mode 09 [01 -> 20].
	def PID0900(self, FreezeIndex = -1):
		Response = self.GetResponse(b'0900\r')
		Response = self.PruneData(Response, 3)
		self.ResolvePidData('09', Response, '00', self.PidDescriptionsMode09)
	PidFunctions["0900"] = PID0900


	def PID0901(self, FreezeIndex = -1):
		return STRING_TODO
	PidFunctions["0901"] = PID0901


# PID0901 Get the VIN Message Count in PID 02.
	def PID0901(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '0901' in self.ValidPIDs:
			Response = self.GetResponse(b'0901\r')
			Response = self.PruneData(Response, 2)
			Result = int(Response, 16)

		return Result
	PidFunctions["0901"] = PID0901


# PID0902 Get the current Vehicle VIN Number from the ECU.
	def PID0902(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '0902' in self.ValidPIDs:
			Response = self.GetResponse(b'0902\r')
			Response = self.PruneData(Response, 3)
			Result = str(bytearray.fromhex(Response).replace(bytes([0x00]), b' '), 'UTF-8')

		return Result
	PidFunctions["0902"] = PID0902


	def PID0903(self, FreezeIndex = -1):
		return STRING_TODO
	PidFunctions["0903"] = PID0903


# PID0903 Get the Calibration ID message count for PID 04.
	def PID0903(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '0903' in self.ValidPIDs:
			Response = self.GetResponse(b'0903\r')
			Response = self.PruneData(Response, 2)
			Result = int(Response, 16)

		return Result
	PidFunctions["0903"] = PID0903


# PID0904 Get the current Calibration ID from the ECU.
	def PID0904(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '0904' in self.ValidPIDs:
			Response = self.GetResponse(b'0904\r')
			Response = self.PruneData(Response, 3)
			Result = str(bytearray.fromhex(Response).replace(bytes([0x00]), b' '), 'UTF-8')

		return Result
	PidFunctions["0904"] = PID0904


	def PID0905(self, FreezeIndex = -1):
		return STRING_TODO
	PidFunctions["0905"] = PID0905


# PID0905 Get Calibration verification numbers (CVN) message count for PID 06.
	def PID0905(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '0905' in self.ValidPIDs:
			Response = self.GetResponse(b'0905\r')
			Response = self.PruneData(Response, 2)
			Result = int(Response, 16)

		return Result
	PidFunctions["0905"] = PID0905


# PID0906 Get the current Calibration Verification Numbers from the ECU.
	def PID0906(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '0906' in self.ValidPIDs:
			Response = self.GetResponse(b'0906\r')
			Result = self.PruneData(Response, 3)

		return Result
	PidFunctions["0906"] = PID0906


	def PID0907(self, FreezeIndex = -1):
		return STRING_TODO
	PidFunctions["0907"] = PID0907


	def PID0908(self, FreezeIndex = -1):
		return STRING_TODO
	PidFunctions["0908"] = PID0908


	def PID0909(self, FreezeIndex = -1):
		return STRING_TODO
	PidFunctions["0909"] = PID0909


# PID0907 Get In-use performance tracking message count for PID 08 and 0B.
	def PID0907(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '0907' in self.ValidPIDs:
			Response = self.GetResponse(b'0907\r')
			Response = self.PruneData(Response, 2)
			Result = int(Response, 16)

		return Result
	PidFunctions["0907"] = PID0907


# PID0908


# PID0909 Get ECU name message count for PID 0A.
	def PID0909(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '0909' in self.ValidPIDs:
			Response = self.GetResponse(b'0909\r')
			Response = self.PruneData(Response, 2)
			Result = int(Response, 16)

		return Result
	PidFunctions["0909"] = PID0909


# PID090A Get the current ECU Name from the ECU.
	def PID090A(self, FreezeIndex = -1):
		Result = STRING_NO_DATA

		if '090A' in self.ValidPIDs:
			Response = self.GetResponse(b'090A\r')
			Response = self.PruneData(Response, 3)
			Result = str(bytearray.fromhex(Response).replace(bytes([0x00]), b' '), 'UTF-8')

		return Result
	PidFunctions["090A"] = PID090A


# PID090B


#/****************************************************************************/
#/* ODBII MODE 0A - Permanent diagnostic trouble codes (DTCs, Cleared DTCs). */
#/****************************************************************************/

