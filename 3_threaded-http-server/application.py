import time
def app(env, start_response):
	start_response('200 OK', [('Content-Type', 'text/html')])
	if 'foo' in env['path'] :
		print "going to sleep"
		time.sleep(5)
	m = "method : " + env['method'] + "<br>"
	p = "path : " + env['path'] + "<br>"
	return [ '<h1>Hello World</h1>', m, p]
	
