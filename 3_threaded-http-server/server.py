#!/usr/bin/env python
import socket, sys, select
import threading
from my_handler import *


TCP_IP = '127.0.0.1'
TCP_PORT = 6060
BUFFER_SIZE = 1024

#create a IPv4 based TCP socket, object 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#attach to the port number
s.bind((TCP_IP, TCP_PORT))

#max client to queue
s.listen(24)

	
print "Starting server..."

try:
	while True:
		#make the connection
		conn, addr = s.accept()
	
		#print client address
		print 'Connection address:', addr
		req_data = ""

		#read all the data from the client
		req_data = conn.recv(BUFFER_SIZE * 4)
		handler = my_handler()
			
		print "Received data..."
		threading.Thread(target=handler, args = (conn, req_data)).start()
		
except KeyboardInterrupt as k:
	print "shutting down server....."
		
except Exception as e:
	print "Something wrong :("
	print e
		
