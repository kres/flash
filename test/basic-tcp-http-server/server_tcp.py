#!/usr/bin/env python
import socket, sys

TCP_IP = '127.0.0.1'
TCP_PORT = 6060
BUFFER_SIZE = 1024

#create a IPv4 based TCP socket, object 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#attach to the port number
s.bind((TCP_IP, TCP_PORT))

#max client to queue
s.listen(1)

#make the connection
conn, addr = s.accept()

#print client address
print 'Connection address:', addr

while 1:
	data = conn.recv(BUFFER_SIZE)
	if not data: break
	print "received data:" 
	sys.stdout.write(repr(data))
	print "**************\n"
	print "sending"
	print "HTTP/1.1 200 OK\r\nContent-type: text/html\r\nContent-Length: 11\r\n\r\nHello World"
	conn.send("HTTP/1.1 200 OK\nContent-type: text/html\nContent-Length: 11\r\n\r\nHello World")  # echo
conn.close()
