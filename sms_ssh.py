#!/usr/bin/python

import ConfigParser
import paramiko
import time

# Connect to the host and execute the commands
# TODO: Resolve host and user outside of this function and send as arguments
# TODO: recv_host should be the IP address. Resolve outside of this function
def ssh_connect(recv_host, cmd_str) :
	ssh = paramiko.SSHClient()

	# TODO: Read hosts from config file
	if recv_host == 'R1' :
		dest_ip = '192.168.1.1'
	elif recv_host == 'R2' :
		dest_ip = '192.168.1.2'

	# Split multi command lines into separate commands (i.e int f0/1; shutdown)
	cmd_list = cmd_str.split(';')

	# Tell paramiko to trust the host
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	# TODO: Whitelist phone-nr -> user/password
	ssh.connect(dest_ip, username='landizz', password='admin')
	chan = ssh.invoke_shell()

	# All commands are executed from global configuration mode (is this good?)
	chan.send('config terminal\n')
	time.sleep(0.2)

	# Send all commands with a pause in between
	for i in cmd_list :
		chan.send(i+'\n')
		time.sleep(0.2)
	
	# TODO: How much data should we get..?
	return chan.recv(4096)
