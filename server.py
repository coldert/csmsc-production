#!/usr/bin/python

from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from urlparse import urlparse, parse_qs
import sms_handling

# Class for BaseHTTPRequestHandler, receives HTTP SMS paths and passes them to be processed.
class GetRequestHandler(BaseHTTPRequestHandler):
	
	# Handle GET requests
	def do_GET(self) : 
		# Parse the requested url and get the query string parameters
		get_path = urlparse(self.path)
		query = parse_qs(get_path.query)
		command = query.get('text', '')[0] if 'text' in query else ''
		originator = query.get('originator', '')[0] if 'originator' in query else ''
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

	# CTRL-C to shutdown HTTP server and the script for the moment.
	except KeyboardInterrupt:	
		print "Server shutdown..."
		httpd.server_close()

# Start the server
RunServerHTTP(80)
