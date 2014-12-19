from http_handler import *
from application import app

class my_handler(http_handler):

	def do_process(self, request):
	
		env = request.headers
		env['method'] = request.command
		env['path'] = self.get_path()
		
		if env['method'] == 'POST':
			env['body'] = self.get_post_content()
		resp_status = []
		
		def start_response(status, headers):
			resp_status.append(int(status[0:3]))
			for k in headers:
				self.set_response_header(k[0], k[1])
			
		resp = app(env, start_response)
		txt = ''
		for r in resp:
			txt += str(r)
			
		return resp_status[0], txt
		
	def do_get(self, request):
		return self.do_process(request)
		
	def do_post(self, request):
		return self.do_process(request)