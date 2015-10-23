#!/usr/bin/python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from urlparse import urlparse, parse_qs
import sms_handling
import logging

logging.basicConfig(filename='csmsc.log', format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG)

# Class for BaseHTTPRequestHandler, receives HTTP SMS paths and passes them to be processed.
class GetRequestHandler(BaseHTTPRequestHandler):
	
	# Handle GET requests
	def do_GET(self) : 
		# Parse the requested url and get the query string parameters
		get_path = urlparse(self.path)
		query = parse_qs(get_path.query)
		# TODO: Query string attributes should be defined 
		#       in config.cfg to handle different gateway providers
		command = query.get('text', '')[0]
		originator = query.get('originator', '')[0]
		# Logging incomming SMS
		logging.info('ORIGINATOR:%s COMMAND:%s', originator, command)
		# Calls the function which notifies the arrival of a SMS
		sms_handling.incoming_sms(command, originator)

# RunServerHTTP start httpd and reports to the handler (GetRequestHandler)
def RunServerHTTP(port) :
	
	# Makes 'httpd' a object, specifices ip:port and the request handler.
	httpd = HTTPServer(('', port), GetRequestHandler)
	try :	
		# Starts HTTP server to receive SMS from SMS Gateway
		print "Listening on port", port
		httpd.serve_forever()
		logging.info('Server started')

	# CTRL-C to shutdown HTTP server and the script for the moment.
	except KeyboardInterrupt:	
		print "Server shutdown..."
		httpd.server_close()
		logging.info('Server stopped')

# Start the server
RunServerHTTP(80)
