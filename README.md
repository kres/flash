# Flash 

**Project Flash** is a collection of various kinds of HTTP servers written in python. Each server essentially does the same thing viz serve HTTP clients, but the *internal implementation* differs vastly. The idea behind this project is to understand the **importance of concurrency and parallelism** in scalable web servers. The project tries to answer a few questions like :

  1. What are the various implementation of web servers currently available?
  2. What kind of web servers would you use when?
  3. What really makes a web server scalable?
  4. Understanding parallelism versus concurrency, and their respective impact on performance.
  5. What are the existing tools available in python to support the building of scalable servers.

To answer the above questions we set out to code our own HTTP servers from scratch. Some sequential, concurrent, parallel, and some a combination of all. Project Flash consists of about a set of 6-7 webservers. Each with it’s own test suite. Before starting to write any web servers, we thoroughly studied and to the best of our efforts tried to understand existing code bases and server side design patterns. Few of the technologies we focused upon is listed below:

* Gunicorn
* tasklets using coroutines in python
* eventlets
* greenlets
* asyncore
* apache mpm’s
* nginx
* node.js runtime

The project source contains of a directory each of every server. Each directory name is preceded by a number indicating the chronological order in which the servers were designed.
  1. Simple HTTP server
  2. Dynamic HTTP server - fork and exec (CGI)
  3. Event based HTTP server (epoll)
  4. Preforked server model (one active connection per worker)
  5. Worker model (workers have threads, one active connection per worker)
  6. Worker model with WSGI support for dynamisim 
  
All the code will be versioned in various folders. ```eg. /server/v1-simple-http/``` so it is easy for the reader to see what modifications have been made, and why a particular version is better than the previous one.

### 1. Simple HTTP server

This is the simplest implementation of a HTTP server, which consists of a sequentially executing, infinite loop which gets the HTTP request, parses it and calls the required handler. 
It consists of the class HTTPServer, which is responsible for all the action. This class can be extended, and do_get, do_post handlers can be overridden to make the http server provide the required functionality.
Pseudo code

```python
Class HTTPServer:

def init:
#initialize data and data streams

def parse_req:
	#parse the incoming response
	#generate key value pairs with req content

def build_response:
	#given the response parameters
	#builds a HTTP response text

def start:
	#open the port, initialize values
	#start the infinite req-resp loop
		# get request from TCP socket
		# call parse_req on it
		# process by calling a callback (do_xyz)
		# call build_response to ready the response string
		# write back to client

def do_get:
	#callback, called when reqd, in the infinite loop

def do_post:
	#callback, called when reqd, in the infinite loop

def do_err:
	#callback, called when reqd, in the infinite loop


Class MyServer extends HTTPServer:
	#override do_get/post/err
Main:
	server = MyServer()
	server.start()
	#now ready to get requests
```

This is the basic pseudo code of the simple HTTP server. The key problem with this is that it can’t handle more than one request simultaneously. Hence if servicing a request takes too long, or if the request is coming in slowly, then all other requests to the server have to be put on hold.

### 2. HTTP CGI Server

With the previous server there was a problem of handling concurrent requests. The CGI server tackles this problem of concurrency. The overall server layout is similar to that of the simple server, the main change is in the infinite processing loop. In the loop, instead of the server process parsing, handling and replying to the requests, it forks and execs a child process to handle the processing and replying of the message. This way the server frees itself from wasting any further time on the request and proceeds to the next request in the pipeline. 

Pseudo code
```
the_req_resp_loop:
#1. get the request, parse it
#2. fork, set IO to TCP socket
#3. set the key-value pair environment
#4. exec the client programs
#5. continue with the loop
```

This is the only change from the previous server architecture. But the problem here is scalability and performance under high load. Forking is a heavy process, one fork for every request consumes valuable memory and time. Plus for persistent connections, we will have to keep the processes around until the connection is cut. This will involve reserving a lot of space and unnecessary scheduling overhead. Hence we need a different way to tackle this problem of scalability.

### 3. Threaded Server

Threads are much lighter  than process to create and maintain. In this model, on every request there is a thread created, instead of forking a process. 

Pseudo code
```
the_req_resp_loop:
#1. get the request, parse it
#2. create a env dict
#3. create new thread for handler
#4. run the handler
#5. continue with the loop
```
The problem with this approach arises when there needs to be a persistent connection. Then lot of threads have to be maintained by the process. Plus threads do not run in parallel in python.


### 4. Epoll based single threaded

This is one of the most efficient and lightweight servers around. It revolves around the concept of kernel supported asynchronous polling via epoll. 
Here multiple connections can be multiplexed on the same thread. That means that one server process can handle thousands of concurrent connections without any context switching overhead.  

Pseudo code
```
open the socket
add it to the list of file_des you are polling for

epoll_loop:
	case action on socket:
		create a new connection
		add it to the list of monitored file_des

	case ‘read’ action:
		get the file causing the trigger, read data from it
		call the read handler based on the data
	
	case ‘write’ action:
		a file_des is now free for writing
		write the data to that file_des
```

The drawback of this method is that while handling one request, if it takes too long, then all other requests are blocked. 
eg. If one request requires you to fetch 3rd party data from another server, then till that is serviced, all other incoming requests are queued, even though the server is sitting idle.

### 5. Threaded epoll server

This is modelled after the classical Event MPM from apache. There is now a pool of threads on which the request runs. the main epoll event loop remains the same, the only difference here is that the handler runs on a different thread. The advantages include multiplexing between requests and no busy waiting. Plus the threads is per request and not per connection. hence you can have 100K connections open at the same time and yet conveniently service only 10K at a time.
