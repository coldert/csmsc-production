#!/usr/bin/python
# Python 2.7.3 script that matches a string against XML document.

import xml.etree.ElementTree as ET
import re

# Parse the XML file to tree.
tree = ET.parse('commands.xml')
root = tree.getroot()

# MAIN FUNCTION
# This function is called by the request handler when an sms is received
def parse(cmd_string):
	# Make string lowercase and split into command parts
	cmd_list = cmd_string.strip().lower().split()

	# Build a search string for etree iterfind function
	xpath_str = ""
	# Lists to hold IP address, interface identifier and other user defined values
	str_ipaddress = []
	str_interface = []
	str_ad = []

	# Build the xpath search string from the command parts, but store ip addresses, 
	# interface identifiers and other user defined values for later
	for cmd in cmd_list:
		# Check if current cmd is an IP address or an interface identifier
		match_ip = re.match("^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/?(\d{1,2})?$", cmd)
		match_int = re.match("^([a-z-]+\d{1,2}(/\d{1,2})*?)$", cmd)
		match_ad = re.match("^ad(\d*)$", cmd)

		if match_ip:
			# Check if the ip address should have a subnet mask
			str_mask = " " + cidr_to_dotted(int(match_ip.group(2))) if (match_ip.group(2)) else "";
			str_ipaddress.append(match_ip.group(1) + str_mask)
		elif match_int:
			str_interface.append(match_int.group(1))
		elif match_ad:
			str_ad.append(match_ad.group(1))
		else:
			# Build each level of xpath search from non user defined values in the command string
			xpath_str += cmd + "/" 

	# Remove the last / from the search string
	xpath_str = xpath_str[:-1]

	# Find XML nodes that match the search string and replace the placeholders with their correct value
	command = root.findtext(xpath_str)
	# Loop through all ip-addresses and interfaces and put the in the right place in the command
	for i in str_ipaddress:
		command = command.replace("#IPADDRESS", i, 1)
	for i in str_interface:
		command = command.replace("#INTERFACE", i, 1)
	for i in str_ad:
		command = command.replace("#AD", i, 1)	
	# Remove all unused placeholders
	command = re.sub(r"#.*\b", "", str(command))
	return command

# Function to convert /24 to 255.255.255.0
# code.activestate.com/recipies/576483-convert-subnetmask-from-cidr-notation-to-dotdecima/
def cidr_to_dotted(mask):
	bits = 0
	for i in xrange(32-mask,32):
		bits |= (1<<i)
	return "%d.%d.%d.%d" % ((bits & 0xff000000) >> 24, (bits & 0xff0000) >> 16, (bits & 0xff00) >> 8, (bits & 0xff))

# Run script with command line argument
if __name__ == "__main__":
	import sys
	print parse(sys.argv[1])