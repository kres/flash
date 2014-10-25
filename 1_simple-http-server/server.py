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

def get_request(data):
	'''Takes the request as a string, returns k-v pairs'''
	print type(data) , data
	#split the content header
	hrs = data.split("\r\n")
	
	#make lists of lists of the headers; [ ['k', 'v'], ['k', 'v']]
	l = map(lambda x : x.split(':', 1), hrs[1:])
	
	#filter unwanted elements such as [ '' ] in the list l; convert it into dict
	req = dict(filter(lambda x : len(x) > 1, l))
	req['method'] = hrs[0].split(' ')[0]
	req['uri'] = hrs[0].split(' ')[1]
	req['protocol'] = hrs[0].split(' ')[2]
	return req

while 1:
	try:
		#make the connection
		conn, addr = s.accept()

		#print client address
		print 'Connection address:', addr
		data = ""
		buf = ""

		#read all the data from the client
		data = conn.recv(BUFFER_SIZE * 4)
			
		print "received data"
		print get_request(data)
		conn.send("HTTP/1.1 200 OK\nContent-type: text/html\nContent-Length: 11\r\n\r\nHello World")  # echo
		conn.close()
		
	except KeyboardInterrupt as k:
		print "shutting down server....."
		break
		
	except Exception as e:
		print "Something wrong :("
		print e	
