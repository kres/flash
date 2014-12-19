import eventlet
from eventlet.green import urllib2

i = 0

def gen():
	i = 1000
	while i :
		i -= 1
		if i % 2:
			yield "http://localhost:6060/bar/good"
		else :
			yield "http://localhost:6060/bar/bad"
		
def fetch(url):
	#print("opening", url)
	body = urllib2.urlopen(url).read()
	#print("done with", url)
	return url, body

urls = gen()

pool = eventlet.GreenPool(100)
for url, body in pool.imap(fetch, urls):
	print("got body from request #" + str(i) + " : ", url, " BODY : ", body)
	i += 1
