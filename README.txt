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
#/* of the program code, SERIAL_PORT_NAME, with the serial port which is    */
#/* to be used. Future verstions of the code should have a graphical        */
#/* interface for configuration and provide more features than just reading */
#/* trouble codes.                                                          */
#/***************************************************************************/

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


Packages required to run the software:
apt-get install python3
apt-get install python3-serial
apt-get install python3-pygame

