#!/usr/bin/python

from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from urlparse import urlparse 
import mainSMS

# Class for BaseHTTPRequestHandler, receives HTTP SMS paths and passes them to be processed.
class GetRequestHandler(BaseHTTPRequestHandler) :
	
	# Handle GET requests
	def do_GET(self) : 
		# Parse the requested url and split the query part of the string into key=value pairs
		get_path = urlparse(self.path)
		query_request = get_path.query.split('&')
		# Calls the function which notifies the arrival of a SMS
		mainSMS.incoming_sms(query_request)

# RunServerHTTP start httpd and reports to the handler (GetRequestHandler)
def RunServerHTTP(port) :
	
	# Makes 'httpd' a object, specifices ip:port and the request handler.
	# TODO: Add server address to config.cfg
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