import socket, sys, os

class HTTPServer():

	def __init__(self, ip='127.0.0.1', port=6060):
		'''creates a HTTPServer object. Initializes it with the requested port number'''
		self.port = port
		self.ip = ip
		self.conn = None

		self.actions = {
				'GET': self.do_get,
				'POST': self.do_post,
				'PUT': self.do_put,
				'HEAD': self.do_head
			}
		
		self.mime_types = {
				'.jpg'	: 'image/jpg',
             			'.gif'		: 'image/gif',
             			'.png'	: 'image/png',
             			'.html'	: 'text/html',
             			'/'		: 'text/html',
            			'.pdf'	: 'application/pdf',
            			'.xml'	: 'application/atom+xml',
            			'.atom'	: 'application/atom+xml'
            		}
            	#the data associated with the latest request
		self.request_data = {}
		
		self.response_headers = { }

		self.response_headers[200] =\
		"""HTTP/1.1 200 OK
		Server: http-server
		"""

		self.response_headers[301] =\
		"""HTTP/1.1 301 Moved
		Server: http-server
		Content-type: text/plain
		Location: %s

		moved
		"""

		self.response_headers[404] =\
		"""HTTP/1.1 404 Not Found
		Server: http-server
		Content-type: text/plain

		"""
		#k-v pairs of content headers to be sent back to server
		#mainly useful only if resp is 200 OK
		self._current_content_header = {}
		
	def _parse_request(self, data):
		'''Takes the request as a string, returns k-v pairs'''
		try:
			#split the content header
			hrs = data.split("\r\n")
			req_header = {}
			req_header['method'] = hrs[0].split(' ')[0]
			req_header['uri'] = hrs[0].split(' ')[1]
			req_header['protocol'] = hrs[0].split(' ')[2]
			if req_header['method'] == 'POST':
				req_body = hrs[-1]
			else:
				req_body = ''
				
			#make lists of lists of the headers; [ ['k', 'v'], ['k', 'v']]
			l = map(lambda x : x.split(':', 1), hrs[1:])
	
			#filter unwanted elements such as [ '' ] in the list l; convert it into dict
			req_header.update( dict(filter(lambda x : len(x) > 1, l)) )
			
			return req_header, req_body
			
		except Exception as e:
			print e
			return None, None
	
	def _build_response(self, resp_code,  data=''):
		'''builds the response, given code,  data'''
		headers = self._current_content_header
		self._current_content_header = {}
			
		if resp_code == 200:
			response = self.response_headers[200]
			response += "Content-Length: " + str(len(data)) + "\r\n"
			
			if not headers.get('Content-type', None):
				#no content-type headers issued
				response += 'Content-type: ' + self.mime_types.get(os.path.splitext(self.request_data['uri'])[1], 'text/plain') + '\r\n'
				
			for k in headers:
				response += k+": "+headers[k] + "\r\n"
			response += '\r\n\r\n'+data
			
		elif resp_code == 301:
			response = self.response_headers[301] % headers['Location']
			
		else:
			response = self.response_headers[404]
		
		return response
			
	
	def set_content_header(key, val):
		'''content header dict creation'''
		self._current_content_header[key] = val
	
	def start(self):
		'''starts the HTTP server'''
		TCP_IP = self.ip
		TCP_PORT = self.port
		BUFFER_SIZE = 1024

		#create a IPv4 based TCP socket, object 
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		#attach to the port number
		s.bind((TCP_IP, TCP_PORT))

		#max client to queue
		s.listen(1)
		
		while 1:
			try:
				#make the connection
				conn, addr = s.accept()

				#print client address
				print 'Connection address:', addr

				#read all the data from the client
				req = conn.recv(BUFFER_SIZE * 4)
				
				#parse the request
				req_header, req_body = self._parse_request(req)
				
				self.request_data = req_header
				self.request_data['body'] = req_body
				
				if req_header:
					print "received data", req_header
					resp_code,  resp_data = self.actions.get(req_header['method'], self.do_error)(req_header, req_body)
					resp = self._build_response(resp_code, resp_data)
					print "Sending" , resp
					conn.send(resp) 
				conn.close()
		
			except KeyboardInterrupt as k:
				print "shutting down server....."
				print k
				break
		
			except Exception as e:
				print "Something wrong :("
				print e
				break
				
			finally :
				conn.close()
	
	def do_get(self, header, body):
		'''called when there is a get request. req is the dict of content header
		returns response header and response body'''
		#pass
		return 200, '<h1>Hello World</h1>'
		
	
	def do_post(self, req, body):
		'''called when there is a get request. req is the dict of content header'''
		pass
	
	def do_head(self, req, body):
		'''called when there is a get request. req is the dict of content header'''
		pass
	
	def do_put(self, req, body):
		'''called when there is a get request. req is the dict of content header'''
		pass	
	
	def do_error(self, req, body):
		'''called when the http verb is unidentified'''
		pass
if __name__ == '__main__':
	server = HTTPServer()
	server.start()
