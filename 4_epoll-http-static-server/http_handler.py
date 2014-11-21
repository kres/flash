from BaseHTTPServer import BaseHTTPRequestHandler
from StringIO import StringIO
import os 

class http_request_parser(BaseHTTPRequestHandler):
	def __init__(self):
		pass 
		
	def parse( self, request_text):
		self.rfile = StringIO(request_text)
		self.raw_requestline = self.rfile.readline()
		self.error_code = self.error_message = None
		self.parse_request()

	def send_error(self, code, message):
		self.error_code = code
		self.error_message = message
        

class http_response_builder():
	
	def __init__(self):
		self.headers = {}
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
            		
            	self.response_code = { }
		self.response_code[200] =\
		"""HTTP/1.1 200 OK\r\nServer: flash-server\r\n"""
		
		self.response_code[404] =\
		"""HTTP/1.1 404 Not Found\r\nServer: flash-server\r\nContent-type: text/plain\r\n"""
		
	def set_header(self, key, value):
		self.handler[key] = value
		
	def build(self, resp_code, response_text='', request_context=None):
		'''builds the response, given code,  data'''
		
		#clear data so that it does not persist for new request
		headers = self.headers
		self.headers = {}
			
		if resp_code == 200:
			response = self.response_code[200]
			response += "Content-Length: " + str(len(response_text)) + "\r\n"
			
			if not headers.get('Content-type', None) and request_context:
				#no content-type headers issued
				response += 'Content-type: ' + self.mime_types.get(os.path.splitext(request_context.path)[1], 'text/plain') + '\r\n'
				
			for k in headers:
				response += k+": "+headers[k] + "\r\n"
			response += '\r\n'+response_text
			
		else:
			response = self.response_code[404]
		
		return response
        
        
        
class http_handler():
	#handles the http stuff
	def __init__(self):
		self.request = http_request_parser()
		self.response = http_response_builder()
		self.actions = {
				'GET': self.do_get,
				'POST': self.do_post
				}
				
	def __call__(self, request_text):
		self.request.parse(request_text)
		
		#bad http request
		if self.request.error_code:
			return False
		
		call_back = self.actions.get(self.request.command.upper(), self.do_error)
		status, response_text = call_back(self.request)
		
		return self.response.build(status, response_text, self.request)
		
	def get_request_header(self, k):
		return self.request.headers.get(k, None)
		
	def set_response_header(self, k, v):
		self.response.headers[k] = v
		
	def get_path(self):
		return self.request.path
	
	def get_version(self):
		return self.request.request_version
		
	def get_post_content(self):
		if self.request.command == 'POST':
			content_len = int(self.request.headers.getheader('content-length', 0))
			post_body = self.rfile.read(content_len) #rfile is a stringIO stream
			return post_body
		
		return ""
		
	def do_get(self, request):
		#pass
		#call back; return (status, data)
		#can modify headers via self.request.headers['xyz']
					#or via request.headers['xyz']
					# or via self.get_request_header
			#response headers set by self.response.headers['abc']= def
					#or via self.set_response_header(k,v)
					
		#RETURN status-code, content
		return 200, "<h1>OK</h1>"
		
	def do_post(self, request):
		return 200, "<h1>OK</h1>"
		#pass
		#call back
		
		
	def do_error(self, request):
		pass
		#call back
		

