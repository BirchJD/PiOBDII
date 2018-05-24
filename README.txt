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
#/* 2018-04-29 V1.01 - Implemented ELM327 class. Finding all valid PIDs.    */
#/*                    Running all valid PIDs and displaying the results.   */
#/*                                                                         */
#/* 2018-05-01 V1.02 - Added initial graphical user interface components.   */
#/*                                                                         */
#/* 2018-05-09 V1.03 - Icons on buttons, lock meters, additional buttons    */
#/*                    and arrange buttons. Tested bluetooth ELM327 device. */
#/*                                                                         */
#/* 2018-05-15 V1.04 - Complete dial gague representation. Save meters      */
#/*                    between application runs. Config font, serial port   */
#/*                    and vehicle. Busy indicator on meter updates. Change */
#/*                    modal operation to a blocking invisible button to    */
#/*                    simplify list selection.                             */
#/*                                                                         */
#/* 2018-05-24 V1.05 - Added Bluetooth pairing description to acompany      */
#/*                    YouTube video, pairing Bluetooth devices on a        */
#/*                    Raspberry Pi. Plus other minor updates.              */
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



REQUIREMENTS (Perform operations here as root user)
============

This project is not supported, the source code is here only to assist others
who would like to adapt it to their own requirements. It has been taken as
far as for the use on a BMW R53 Mini Cooper S, any additional adaptions,
modifications and supported data will be requrired to make use for other
vehicles.

This application has been tested with a USB ELM327 OBDII cable and a
Bluetooth ELM327 OBDII dongle.

This application has been tested intended to run on a Raspberry Pi.
The following versions and packages where present when tested:

cat /proc/version 
	Linux version 4.14.34-v7+ (dc4@dc4-XPS13-9333)
	(gcc version 4.9.3 (crosstool-NG crosstool-ng-1.22.0-88-g8460611))
	#1110 SMP Mon Apr 16 15:18:51 BST 2018


# Packages required to run the software:
apt-get install python3
apt-get install python3-serial
apt-get install python3-pygame
apt-get install python3-pypdf2
apt-get install python3-reportlab

# If you are running Raspbian lignt, you will also need the following to
# provide a minimal GUI environment.
# On a 4GB SD card after install 1685452 (~1.6GB) used and 1860924(~1.8GB) free:
apt-get install xserver-xorg
apt-get install xserver-xorg-input-mouse
apt-get install xserver-xorg-input-kbd
apt-get install xserver-xorg-video-*
apt-get install lxdm

# Optional for printer support, currently untested:
apt-get install lpr

# Optional for opening and reading PDF files from Raspbian:
apt-get install evince


# Packages for Bluetooth serial dongle:
apt-get install bluez
apt-get install bluetoothd


Start application from the command line:
./PiOBDII.py
OR:
python3 PiOBDII.py



ADDING MISSING PID SUPPORT
==========================

PID codes supported by a BMW Mini Cooper S R53 have been provided for in this
source code. Additional PID code support may have been added over time. But
for other vehicles there may be missing supported PID codes. To add support
for a PID code, add the PID code to the EML327 class using existing PID source
code as a guide. And check the formatting of the data in the PID text file
definitions.

What does this mean for other vehicles:

The trouble code reporting is standard to the OBDII protocol. So trouble code
reporting should work. There are standard ISO trouble code descriptions which
apply to all vehicles, these descriptions are present, and will be displayed
with the trouble codes reported. Vehicle specific trouble codes will be
reported, but with the description "[NO DESCRIPTION]", so you will still see
the trouble code numbers which you can look up, or provide a lookup table for
your own vehicle.

The most common PIDs are supported, such as vehicle speed, engine speed, engine
temperature, ... Any unsupported PIDs should appear with an unsupported message.
You should be able to add them in the ELM327.py file. I am unlikely to have
time to add them, but you can report them as missing and if I have time I will
attempt to add them if you reply as to if they are working correctly after.



REFERENCE
=========

Source code can be found here:
http://www.github.com/BirchJD/PiOBDII/


Reference videos can be found here:

Raspberry Pi OBDII Bluetooth Vehicle Diagnostic Tablet
https://youtu.be/yTRAhubZhsU

Reading All OBDII PID Data For A BMW Mini Using A Python Script
https://youtu.be/JOTc_qhx6rQ

The Raspberry Pi OBDII Python script is now communicating and getting all valid PID data using a Python Class. Source code will be updated on GitHub.
https://youtu.be/JOTc_qhx6rQ

Reading OBDII Trouble Codes & Descriptions Using Python On A Raspberry Pi
https://youtu.be/3HDXC85-MFU

Raspberry Pi OBDII Connection To ECU Via ELM327
Using a Raspberry Pi to Talk OBDII to an ECU Via an ELM327 Device
https://youtu.be/NvYXtQmOYDw

Brief Overview of CAN BUS Preparation For ODBII
https://www.youtube.com/watch?v=JHP_yXznV2Q



BLUETOOTH DONGLE (Perform operations here as root user)
================

EXAMPLE CONNECTING TO A BLUETOOTH ELM327 DONGLE FROM LINUX COMMAND LINE
OR THE BUILT IN RASPBERRY PI 3 BLUETOOTH DEVICE:


# Bluetooth service
# -----------------

# Get the status of the Bluetooth service.
service bluetooth status

# If the Bluetooth service is not running, start it.
service bluetooth start

# Stop the Bluetooth service only if required.
service bluetooth stop


# Pairing a Bluetooth device
# --------------------------

# Once a device is paired it should automatically pair in future.

# Start the Bluetooth utility.
bluetoothctl

# Make sure the Bluetooth device is powered on.
power on

# Make sure an agent is running for the Bluetooth device.
agent on

# Start a scan for other Bluetooth devices in the area.
scan on

# Wait for the required Bluetooth device to be reported...

# Stop scanning when the required Bluetooth device is found.
scan off

# Attempt to pair the required Bluetooth device.
pair <dev>

e.g. <dev>=00:1D:A5:F7:FF:0D

# Pairing normally prompts for a password. Standard Bluetooth pairing passwords
# are: 0000 or 1234, try these if you are unsure of the password.

# If parinig fails or propt for password does not appear, try the following, and
# then try paring again.
agent off
power off
power on
agent on

# Once paired it should appear in the list of paired devices.
paired-devices

# You can now leave the Bluetooth utility and the device should be paired and
# ready for use.
quit


# Creating a serial device for use in the OBDII application
# ---------------------------------------------------------

# rfcomm associates the paired device ID with a serial device name.
rfcomm bind 0 <dev>

# The device it should create is:
/dev/rfcomm0

# To remove the serial device do the following if required.
rfcomm release <dev>

### Shouldn't need this command, force rfdevices to stop.
### rfkill list


# Unpairing a Bluetooth device
# ----------------------------

# Start the Bluetooth utility.
bluetoothctl

# Unpair the Bluetooth device if required.
remove <dev>

# Make sure the agent is stopped for the Bluetooth device.
agent off

# Make sure the Bluetooth device is powered down.
power off

# Exit the Bluetooth utility.
quit



TODO
====
Drag scroll text.

Data acquisition increase speed.
Plot data on report.
Meter Data Array Index Selector.
Test data for all data types.

