import time, random
def app(env, start_response):
	start_response('200 OK', [('Content-Type', 'text/html')])
	if 'bad' in env['path'] :
		time.sleep(random.uniform(0,1))
	m = "method : " + env['method'] + "<br>"
	p = "path : " + env['path'] + "<br>"
	return [ '<h1>Hello World</h1>', m, p]
	
