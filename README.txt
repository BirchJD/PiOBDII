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
#/* Raspberry Pi ELM327 ODBII CAN BUS Diagnostic Software.                  */
#/*                                                                         */
#/* (C) Jason Birch 2018-04-27 V1.00                                        */
#/*                                                                         */
#/* Initial OBDII Python application to read trouble codes from the ECU and */
#/* display each trouble code along with it's human readable description.   */
#/*                                                                         */
#/* In this initial version, the user must update the constant at the top   */
#/* of the EML327 class, SERIAL_PORT_NAME, with the serial port which is    */
#/* to be used. Future verstions of the code should have a graphical        */
#/* interface for configuration and provide more features than just reading */
#/* trouble codes.                                                          */
#/***************************************************************************/

==============================================================================
WARNING: Trouble codes and descriptions supplied with this source code have
been obtained from various sources and reformatted for use in this
application. The original data may be erronious and the reformatting
process may have introduced errors into the codes or descriptions. The ties
between the codes and the descriptions may also have been effected and
made erronious. As such any part of this software or data may provide
invalid or misguiding data or cause harm. Use this software and data at
your own risk, no garentees or warrenties are provided with the software
and data and absolutly no responsibility will be taken for and issues or
damage caused during the installation or use of the software or data.

Never use a vehicle on a public road with a device connected to the OBDII
port or any other part of the CAN BUS. The CAN BUS is used to run the engine,
any issues on the CAN BUS while the engine is running may effect the running
of the engine or even damage the engine.
==============================================================================



Packages required to run the software:
apt-get install python3
apt-get install python3-serial
apt-get install python3-pygame



Packages for Bluetooth serial dongle:
apt-get install bluez
apt-get install bluetoothd



EXAMPLE CONNECTING TO A BLUETOOTH ELM327 DONGLE FROM LINUX:
service bluetooth start

bluetoothctl
power on
agent on
scan on
scan off
pair <dev>

e.g. <dev>=00:1D:A5:F7:FF:0D

rfcomm bind 0 <dev>
rfcomm
/dev/rfcomm0
rfcomm release <dev>

bluetoothctl
remove <dev>
agent off
power off

service bluetooth stop



TODO
====
Drag scroll text.
Min/Max values on meters.
Auto scale or wrap text on gadgits.

Save meter config.
Numeric scales on gadgits.
Config dialog.
	Serial device select.
	Vehicle select.
	Font select.

Freeze frame data.
PDF summary.
Print summary.
Plot data points.
	Select plot data types.
	Save plot config.
Test data for all data types.

