#!/usr/bin/python

import sms_ssh
import sms_tolk
from urllib import unquote, quote

# Function gets called from smsIO
# by the handler when a GET request has been made. 
def incoming_sms(query_list):
	
	# Split query string into parts
	for i in query_list:
		part = i.split('=')
		if part[0] == 'text': command_string = unquote(part[1])
		if part[0] == 'originator': originator = unquote(part[1])
		if part[0] == 'destination': destination = unquote(part[1])

	# Split command_string into HOST and COMMAND parts
	# TODO: What happens if no HOST is included?
	(command_host, command) = command_string.split('!')

	# Parse COMMAND into actual Cisco IOS Commands
	complete_cmd_string = sms_tolk.parse(command)

	# Send a command to a host via SSH and returns the output
	recv_host_output = sms_ssh.ssh_connect(command_host, complete_cmd_string)
	
	# Send a reply to the user via the sms gateway
	# TODO: USER/PASS defined in config file
	#send_sms(originator, recv_host_output, CELLSYNT_USER, CELLSYNT_PASS)

# Function for sending SMS data back to the SMS gateway for handling
def send_sms(recv, msg, user, passw):
	
	# Specifices settings for the SMS Gateway. NOTE: Can be modified and add other settings, check SMS Gateway API
	gateway_url = "se-1.cellsynt.net"
	gateway_file = "/sms.php?"
	charset = "charset=UTF-8"

	# Adds the data to the their respective attribute of the HTTP path.
	username = 'username=' + user
	password = 'password=' + passw
	dest = 'destination=' + recv
	text = 'text=' + quote(msg)
	
	# Makes the PATH for the GET message
	gateway_request = gateway_file + username + '&' + password + '&' + dest + '&' + charset + '&' + text
	print gateway_request	
	# Working HTTP GET, 'gateway_url' is the url from which you want to use GET on. NOTE: Tested against 'https://docs.python.org/2/'
	http_connection = httplib.HTTPConnection(gateway_url)
	
	# Calling a function of the http connection object, from which we use GET with the specified path('gateway_request')
	http_connection.request('GET', gateway_request)

	# Gets the response, used for testing. Might be useful for checking status of the HTTP receiver.
	# TODO: We should log all sent messages
	connection_response = http_connection.getresponse()
	print connection_response.status, connection_response.msg
