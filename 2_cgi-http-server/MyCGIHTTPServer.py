#!/usr/bin/env python

import os
import sys
import urllib
import BaseHTTPServer
import SimpleHTTPServer

class MyCGIHTTPRequestHandler (SimpleHTTPServer.SimpleHTTPRequestHandler):
	
	#Default directories to look for CGI scripts.
	cgi_directories = ['/cgi-bin', '/htbin']
	
	have_fork = hasattr(os, 'fork')
	rbufsize = 0
	
	def send_head(self):
		"""	Version of send_head that support CGI scripts.
		Overrides the method send_head in SimpleHTTPRequestHandler. """
		
		#If it is a CGI script, execute it, otherwise, call the send_head function of the superclass.
		if self.is_cgi():
			return self.run_cgi()
		else:
			return SimpleHTTPServer.SimpleHTTPRequestHandler.send_head(self)

	def is_cgi(self):
		""" Test whether self.path corresponds to a CGI script.
		Returns a tuple (dir, rest) if self.path requires running a CGI script, None if not.  
		Ex. If the URL = http://localhost:8080/foo/bar/test.py?a=one&b=two, then
			self.path = /foo/bar/test.py?a=one&b=two, and
			dir = /foo/bar and rest = /test.py?a=one&b=two
		Tests whether the path begins with one of the strings in the list
		self.cgi_directories (and the next character is a '/'or the end of the string). """
		
		path = self.path
		for x in self.cgi_directories:
			i = len(x)
			if path[:i] == x and (not path[i:] or path[i] == '/'):
				self.cgi_info = path[:i], path[i+1:]
				return 1
		return 0
  
	def is_executable(self, path):
		""" Test whether the argument path is an executable file."""
		
		return executable(path)

	def is_python(self, path):
		""" Test whether argument path is a Python script, using os.path.splitext() 
		This splits the given path into a tuple, (root, ext), ext is empty or begins with a period and contains at most one period.
		Ex. os.path.splitext('/foo/bar/text.py') returns ('/foo/bar/text', '.py')
		"""
		
		head, tail = os.path.splitext(path)
		return tail.lower() in (".py", ".pyw")

	def run_cgi(self):
		
		""" Execute a CGI script. """
		
		# Get the information assigned in the is_cgi call, ie. directory and filename[+ query string]
		dir, rest = self.cgi_info
		
		# Separate the query string from the name of the file.
		i = rest.rfind('?')
		
		if i >= 0:
			rest, query = rest[:i], rest[i+1:]
		else:
			query = ''
		
		# Remove the leading '/' from the name of the script if it exists.
		i = rest.find('/')
		if i >= 0:
			script, rest = rest[:i], rest[i:]
		else:
			script, rest = rest, ''
		
		# Compose the full path of the script. 
		scriptname = dir + '/' + script
		
		# Translate it from /-separated to the local filesystem syntax using SimpleHTTPRequestHandler.translate_path()
		scriptfile = self.translate_path(scriptname)
		
		if not os.path.isfile(scriptfile):
			self.send_error(403, "CGI script is not a plain file (%s)" % `scriptname`)
			return
		
		# Checking if the file exists.
		if not os.path.exists(scriptfile):
			self.send_error(404, "No such CGI script (%s)" % `scriptname`)
			return
			
		# Checking if the script is an executable python script.
		ispy = self.is_python(scriptname)
		if not ispy:
			if not (self.have_fork):
				self.send_error(403, "CGI script is not a Python script (%s)" % `scriptname`)
				return
			if not self.is_executable(scriptfile):
				self.send_error(403, "CGI script is not executable (%s)" % `scriptname`)
				return
		
		# Setting up the environment for running the cgi script.
		env = {}
		
		env['SERVER_SOFTWARE'] = self.version_string()
		env['SERVER_NAME'] = self.server.server_name
		env['GATEWAY_INTERFACE'] = 'CGI/1.1'
		env['SERVER_PROTOCOL'] = self.protocol_version
		env['SERVER_PORT'] = str(self.server.server_port)
		env['REQUEST_METHOD'] = self.command
		
		uqrest = urllib.unquote(rest)
		env['PATH_INFO'] = uqrest
		env['PATH_TRANSLATED'] = self.translate_path(uqrest)
		env['SCRIPT_NAME'] = scriptname
		
		if query:
			env['QUERY_STRING'] = query
		
		host = self.address_string()
		if host != self.client_address[0]:
			env['REMOTE_HOST'] = host
		
		env['REMOTE_ADDR'] = self.client_address[0]
		
		if self.headers.typeheader is None:
			env['CONTENT_TYPE'] = self.headers.type
		else:
			env['CONTENT_TYPE'] = self.headers.typeheader
		
		length = self.headers.getheader('content-length')
		if length:
			env['CONTENT_LENGTH'] = length
		
		accept = []
		for line in self.headers.getallmatchingheaders('accept'):
			if line[:1] in "\t\n\r ":
				accept.append(line.strip())
			else:
				accept = accept + line[7:].split(',')
		env['HTTP_ACCEPT'] = ','.join(accept)
		
		ua = self.headers.getheader('user-agent')
		if ua:
			env['HTTP_USER_AGENT'] = ua
			
		co = filter(None, self.headers.getheaders('cookie'))
		if co:
			env['HTTP_COOKIE'] = ', '.join(co)
		
		# Other HTTP_* headers
		
		if not self.have_fork:
			# Since we're setting the env in the parent, provide empty values to override previous ones.
				for k in ('QUERY_STRING', 'REMOTE_HOST', 'CONTENT_LENGTH', 'HTTP_USER_AGENT', 'HTTP_COOKIE'):
					env.setdefault(k, "")
		
		self.send_response(200, "Script output follows")
		
		decoded_query = query.replace('+', ' ')
		
		# For Unix systems - fork as we should.
		if self.have_fork:
			args = [script]
			if '=' not in decoded_query:
				args.append(decoded_query)
			nobody = nobody_uid()
			
			self.rfile.flush() # Always flush before forking
			self.wfile.flush() # Always flush before forking
			
			pid = os.fork()
			
			# In the parent...
			if pid != 0:
				pid, sts = os.waitpid(pid, 0)
				if sts:
					self.log_error("CGI script exit status %#x", sts)
				return
			
			# In the child...
			try:
				try:
					os.setuid(nobody)
				except os.error:
					pass
				
				os.dup2(self.rfile.fileno(), 0)
				os.dup2(self.wfile.fileno(), 1)
				os.execve(scriptfile, args, env)
			except:
				self.server.handle_error(self.request, self.client_address)
				os._exit(127)
		else:
			os.environ.update(env)
			save_argv = sys.argv
			save_stdin = sys.stdin
			save_stdout = sys.stdout
			save_stderr = sys.stderr
			
			try:
				try:
					sys.argv = [scriptfile]
					
					if '=' not in decoded_query:
						sys.argv.append(decoded_query)
					
					sys.stdout = self.wfile
					sys.stdin = self.rfile
					
					execfile(scriptfile, {"__name__": "__main__"})
				finally:
					sys.argv = save_argv
					sys.stdin = save_stdin
					sys.stdout = save_stdout
					sys.stderr = save_stderr
			except SystemExit, sts:
				self.log_error("CGI script exit status %s", str(sts))
			else:
				self.log_message("CGI script exited OK")

nobody = None

def nobody_uid():
	""" Internal routine to get nobody's uid. 
	This enables the server to run with no priveliges at all, for security reasons.
	"""
	global nobody
	
	if nobody:
		return nobody
	
	try:
		import pwd
	except ImportError:
		return -1
	
	try:
		nobody = pwd.getpwnam('nobody')[2]
	except KeyError:
		nobody = 1 + max(map(lambda x: x[2], pwd.getpwall()))
	
	return nobody
	
def executable(path):
	""" Test permissions for executable file. """
	try:
		st = os.stat(path)
	except os.error:
		return 0
	
	return st[0] & 0111 != 0

def test(HandlerClass = MyCGIHTTPRequestHandler,ServerClass = BaseHTTPServer.HTTPServer):
	SimpleHTTPServer.test(HandlerClass, ServerClass)

if __name__ == '__main__':
	test()
