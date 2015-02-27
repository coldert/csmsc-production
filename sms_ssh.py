#!/usr/bin/python

import paramiko
import time

# Connect to the host and execute the commands
def ssh_connect(recv_host, cmd_str, username, password):

	# Split multi command lines into separate commands (i.e int f0/1; shutdown)
	cmd_list = cmd_str.split(';')

	ssh = paramiko.SSHClient()

	# Tell paramiko to trust the host
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	# Set up connection to host
	ssh.connect(dest_ip, username, password)
	# Open a shell
	chan = ssh.invoke_shell()

	# All commands are executed from global configuration mode
	chan.send('config terminal\n')
	time.sleep(0.2)

	# Send all commands with a pause in between
	for i in cmd_list :
		chan.send(i + '\n')
		# Give the device some time to execute the command
		time.sleep(0.2)
	
	# TODO: How much data should we get..?
	return chan.recv(4096)
