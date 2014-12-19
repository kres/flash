num_servers = 4

for i in range(num_servers):
	execfile('epoll_server.py')
