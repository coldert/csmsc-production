#!/usr/bin/python

import ConfigParser
import httplib
from urllib import unquote, quote
import sms_ssh
import sms_tolk
import re

# Read main configuration file
conf = ConfigParser.ConfigParser()
conf.read('config.cfg')

# Function gets called from smsIO
# by the handler when a GET request has been made. 
def incoming_sms(command_string, originator_string):
	
	# Split command_string into HOST and COMMAND parts
	# TODO: What happens if no HOST is included?
	(command_host, command) = command_string.split('!')
	# Parse command string into actual Cisco IOS commands
	complete_cmd_string = sms_tolk.parse(command)
	
	# originator must be in format 0046XXXXXXXXXXX
	originator = parse_phone(originator_string) if originator_string != "" else None

	# Send a command to a host via SSH and returns the output
	try:
		recv_host_output = sms_ssh.ssh_connect(command_host, complete_cmd_string)
	except Exception as e:
		recv_host_output = "Something went wrong. " + str(e.errno) + ": " + e.strerror
		
	# Send a reply to the user via the sms gateway
	if originator:
		print "SENDING SMS..."
		#send_sms(originator, recv_host_output, conf.get('cellsynt','user'), conf.get('cellsynt','pass'))
	else:
		print "NO ORIGINATOR"
	print recv_host_output

# Parse phone number
def parse_phone(phone_number):
	# Make sure the number start with exactly two zeroes
	return "00" + re.sub('^0*', '', phone_number)
	
# Function for sending SMS data back to the SMS gateway for handling
def send_sms(recv, msg, user, passw):

	# Adds the data to the their respective attribute of the HTTP path.
	username = 'username=' + user
	password = 'password=' + passw
	dest = 'destination=' + recv
	text = 'text=' + quote(msg)
	
	# Makes the PATH for the GET message
	gateway_request = "/" + conf.get('cellsynt','gateway_file') + username + '&' + password + '&type=text&' + dest + '&charset=' + conf.get('cellsynt','charset') + '&' + text
	print gateway_request
	# Working HTTP GET, 'gateway_url' is the url from which you want to use GET on. NOTE: Tested against 'https://docs.python.org/2/'
	http_connection = httplib.HTTPConnection(conf.get('cellsynt','gateway_url'))
	# Calling a function of the http connection object, from which we use GET with the specified path('gateway_request')
	http_connection.request('GET', gateway_request)

	# Gets the response, used for testing. Might be useful for checking status of the HTTP receiver.
	# TODO: We should log all sent messages
	connection_response = http_connection.getresponse()
	if connection_response.status != 200:
		print "SMS not sent.", connection_response.msg
	else:
		print "SMS sent successfully."

# Run script with command line argument (for testing purposes)
if __name__ == "__main__":
	import sys
	print incoming_sms(sys.argv[1], sys.argv[2])