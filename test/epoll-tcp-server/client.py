import socket

TCP_IP = '127.0.0.1'
TCP_PORT = 6060
BUFFER_SIZE = 1024
MESSAGE = "ab"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send('x')
import time
time.sleep(3)
s.send('y')
data = s.recv(BUFFER_SIZE)
print "received data:", data
while True:
	pass
s.close()



