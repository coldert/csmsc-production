#!/usr/bin/python

from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from urlparse import urlparse 
import httplib
import mainSMS

# Class for BaseHTTPRequestHandler, receives HTTP SMS paths and passes them to be processed.
class GetRequestHandler(BaseHTTPRequestHandler) :
	
	# This is specifically for GET requests
	def do_GET(self) : 
		# Input the requested GET path of the url to a variable
		get_path = urlparse(self.path)
		# Takes the query part of the string and splits it.
		query_request = get_path.query.split('&')
		# Calls the function which notifies the arrival of a SMS
		mainSMS.incoming_sms(query_request)

# RunServerHTTP start httpd and reports to the handler (GetRequestHandler)
def RunServerHTTP(port) :
	
	# Makes 'httpd' a object, specifices ip:port and the request handler.
	httpd = HTTPServer(('', port), GetRequestHandler)
	try :	
		# Starts HTTP server to receive SMS from SMS Gateway
		print "Listening on port", port
		httpd.serve_forever()

	# CTRL-C to shutdown HTTP server and the script for the moment.
	except :	
		print "Server shutdown..."
		httpd.server_close()

RunServerHTTP(80)