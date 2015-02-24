#!/usr/bin/python

import ConfigParser
import httplib
from urllib import unquote, quote
import sms_ssh
import sms_tolk

conf = ConfigParser.ConfigParser()
conf.read('config.cfg')

# Function gets called from smsIO
# by the handler when a GET request has been made. 
def incoming_sms(query_list):
	
	# Split query string into parts
	# TODO: Is there a better way?
	for i in query_list:
		part = i.split('=')
		if part[0] == 'text': command_string = unquote(part[1])
		if part[0] == 'originator': originator = part[1]
		if part[0] == 'destination': destination = part[1]

	# Split command_string into HOST and COMMAND parts
	# TODO: What happens if no HOST is included?
	(command_host, command) = command_string.split('!')

	# Parse COMMAND into actual Cisco IOS commands
	complete_cmd_string = sms_tolk.parse(command)

	# Send a command to a host via SSH and returns the output
	try:
		recv_host_output = sms_ssh.ssh_connect(command_host, complete_cmd_string)
	except Exception as e:
		recv_host_output = "Something went wrong. " + str(e.errno), e.strerror
		
	# Send a reply to the user via the sms gateway
	# Receiver must be in format 0046XXXXXXXXXXX
	# TODO: Make function to parse phone number (add 00 if not present)
	#send_sms('00'+originator, recv_host_output, conf.get('cellsynt','user'), conf.get('cellsynt','pass'))
	print recv_host_output

# Function for sending SMS data back to the SMS gateway for handling
def send_sms(recv, msg, user, passw):

	# Adds the data to the their respective attribute of the HTTP path.
	username = 'username=' + user
	password = 'password=' + passw
	dest = 'destination=' + recv
	text = 'text=' + quote(msg)
	
	# Makes the PATH for the GET message
	gateway_request = conf.get('cellsynt','gateway_file') + username + '&' + password + '&type=text&' + dest + '&charset=' + conf.get('cellsynt','charset') + '&' + text
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
