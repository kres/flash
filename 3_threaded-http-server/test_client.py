import socket

TCP_IP = '127.0.0.1'
TCP_PORT = 6060
BUFFER_SIZE = 1024
MESSAGE = '''GET /foo/bar HTTP/1.1
Host: api.opencalais.com
Content-Type: text/xml; charset=utf-8'''

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send(MESSAGE)
data = s.recv(BUFFER_SIZE)
print "received data : "
print data
s.close()

