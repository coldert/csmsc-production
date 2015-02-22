#!/usr/bin/python

import ConfigParser
import paramiko
import time

def ssh_connect(recv_host, cmd_str) :
	ssh = paramiko.SSHClient()

	# TODO: Read hosts from config file
	if recv_host == 'R1' :
		dest_ip = '192.168.1.1'
	elif recv_host == 'R2' :
		dest_ip = '192.168.1.2'

	cmd_list = cmd_str.split(';')

	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	# TODO: Whitelist phone-nr -> user/password
	ssh.connect(dest_ip, username='landizz', password='admin')

	chan = ssh.invoke_shell()

	chan.send('config terminal\n')
	time.sleep(0.2)

	for i in cmd_list :
		chan.send(i+'\n')
		time.sleep(0.2)
		
	return chan.recv(4096)
