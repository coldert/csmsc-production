#!/usr/bin/python

import ConfigParser
import httplib
from urllib import unquote, quote
import sms_ssh
import sms_tolk
import re

# Read configuration file
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
	print complete_cmd_string #DEBUGGING
	
	# originator must be in format 0046XXXXXXXXXXX
	originator = parse_phone(originator_string) if originator_string != "" else None
	(username, password) = get_credentials(originator)
	host_ip = get_host_ip(command_host)
	print username, password, host_ip #DEBUGGING

	# Send a command to a host via SSH and returns the output
	try:
		recv_host_output = sms_ssh.ssh_connect(host_ip, complete_cmd_string, username, password)
	except Exception as e:
		recv_host_output = "Something went wrong."
		
	# Send a reply to the user via the sms gateway
	if originator:
		print "SENDING SMS..."
		#send_sms(originator, recv_host_output, conf.get('smsgateway', 'user'), conf.get('smsgateway', 'pass'))
	else:
		print "NO ORIGINATOR"
	print recv_host_output

# Parse phone number
def parse_phone(phone_number):
	# Make sure the number start with exactly two zeroes
	return "00" + re.sub('^0*', '', phone_number)
	
# Get username/password from list of phonenumbers
def get_credentials(phone_number):
	user = conf.get('users', phone_number)
	return user.split(':') if user else []

# Get host IP from list of hostnames
def get_host_ip(hostname):
	host = conf.get('hosts', hostname)
	return host if host else None

# Function for sending SMS data back to the SMS gateway for handling
def send_sms(recv, msg, user, passw):

	# Adds the data to the their respective attribute of the HTTP path.
	username = 'username=' + user
	password = 'password=' + passw
	dest = 'destination=' + recv
	text = 'text=' + quote(msg)
	
	# Makes the PATH for the GET message
	gateway_request = "/" + conf.get('smsgateway', 'gateway_file') + username + '&' + password + '&type=text&' + dest + '&charset=' + conf.get('smsgateway', 'charset') + '&' + text
	print gateway_request
	# Working HTTP GET, 'gateway_url' is the url from which you want to use GET on. NOTE: Tested against 'https://docs.python.org/2/'
	http_connection = httplib.HTTPConnection(conf.get('smsgateway', 'gateway_url'))
	# Calling a function of the http connection object, from which we use GET with the specified path('gateway_request')
	http_connection.request('GET', gateway_request)

	# Gets the response, used for testing. Might be useful for checking status of the HTTP receiver.
	# TODO: We should log all sent messages
	connection_response = http_connection.getresponse()
	if connection_response.status != 200:
		print "SMS not sent.", connection_response.msg
	else:
		print "SMS sent successfully."
