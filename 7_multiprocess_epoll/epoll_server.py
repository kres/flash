#!/usr/bin/env python
import socket, sys, select
import threading 
from wsgi_handler import *

TCP_IP = 'localhost'
TCP_PORT = 6060
BUFFER_SIZE = 1024
ANY_ERR = select.EPOLLHUP | select.EPOLLERR | select.EPOLLIN

def server_process():
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
						handler = wsgi_handler()
					
						#let a new thread handle
						threading.Thread(target=handler, args = (connections[fileno], requests[fileno])).start()
						epoll.unregister(fileno)
						connections.pop(fileno)
						requests.pop(fileno)
						responses.pop(fileno)
					
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
		
		
if __name__ == '__main__':
	import multiprocessing as mp
	import signal
	
	def sigchld_handler(signum, stack):
		print "child dead"
		mp.Process(target=server_process).start()

	signal.signal(signal.SIGCHLD, sigchld_handler)
	processes = [mp.Process(target=server_process) for x in range(4)]

	# Run processes
	for p in processes:
	    p.start()

	# Exit the completed processes
	for p in processes:
	    p.join()
