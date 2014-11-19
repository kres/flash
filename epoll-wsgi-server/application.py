def app(env, start_response):
	start_response('200 OK', [('Content-Type', 'text/html')])
	m = "method : " + env['method'] + "<br>"
	p = "path : " + env['path'] + "<br>"
	return [ '<h1>Hello World</h1>', m, p]
	
