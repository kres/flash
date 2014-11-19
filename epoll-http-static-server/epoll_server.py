#!/usr/bin/env python
import socket, sys, select
from http_handler import *

#def handler(req):
#	if len(req) == 1:
#		return False
#	return str.upper(req)

TCP_IP = '127.0.0.1'
TCP_PORT = 6060
BUFFER_SIZE = 1024
ANY_ERR = select.EPOLLHUP | select.EPOLLERR | select.EPOLLIN

#create a IPv4 based TCP socket, object 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#attach to the port number
s.bind((TCP_IP, TCP_PORT))

#max client to queue
s.listen(24)

#set the socket type to non blocking
s.setblocking(0)

#create the epoll object
epoll = select.epoll()

#add the server socket to be monitored by 
epoll.register(s.fileno(), select.EPOLLIN)

#keeps the fd to conn object mapping
connections = {}

#fd to "what has been read till now from the stream" mapping
requests = {}

#the fd to response mapping, what is to be written into the fd.
responses = {}
try:
	#try the following indefinately
	print "entering loop"
	while True:
		#wait to eternity for an event
		events = epoll.poll()
		print "events occured", events
		
		#when events occur
      		for fileno, event in events:
      			
      			#if the event occured on the socket
        		if fileno == s.fileno():
        			print "an conn request event occured"
        			#accept the connection
				conn, add = s.accept()
				print "connection accepted at", add, "with FD :", conn.fileno()
				conn.setblocking(0)
				
				#register the new conn, populate fields
				epoll.register(conn.fileno(), select.EPOLLIN | select.EPOLLERR)
				connections[conn.fileno()] = conn
				requests[conn.fileno()] = ''
				responses[conn.fileno()] = ''
				
			#incase of read event on a connection
			elif event == select.EPOLLIN:
				print "a data request event occured"
				#TODO : read all bytes available, not only 1024
				req_data = connections[fileno].recv(1024)
				
				if not req_data:
					#client closed, cleanup
					print "Client connection closed"
					epoll.unregister(fileno)
					connections[fileno].close()
					connections.pop(fileno)
					requests.pop(fileno)
					responses.pop(fileno)
					
				else:
					requests[fileno] += req_data
					print 'req : ', requests[fileno]
					#call the handler
					handler = http_handler()
					res = handler(requests[fileno])
				
					#if more data is still there res -> False; else res is response str
					if res:
						#clear the current request, as it's been processed
						requests[fileno] = '' 
						#change monitoring event
						epoll.modify(fileno, select.EPOLLOUT | ANY_ERR)
						#fill in the responses
						responses[fileno] = res
						print 'response', res
			
			#when connection becomes writable
			elif event == select.EPOLLOUT:
				print "a writeable event occured"
         			bytes_written = connections[fileno].send(responses[fileno])
				responses[fileno] = responses[fileno][bytes_written:]
				
				#incase all bytes have been written
				if len(responses[fileno]) == 0:
					responses[fileno] = ''
					#go back for input
					epoll.modify(fileno, select.EPOLLIN | ANY_ERR)
					
			elif event == ANY_ERR:
				print "an connection hangup event occured"
				epoll.unregister(fileno)
				connections[fileno].close()
				connections.pop(fileno)
				requests.pop(fileno)
				responses.pop(fileno)

except Exception as e:
	print "error occured : " , e
	
except KeyboardInterrupt as e:
	print "shutting down server"  
	
finally:
	epoll.unregister(s.fileno())
	epoll.close()
	s.close()
