Flash
=====

A python framework written from scratch with love. Unlike other python frameworks (like twisted, Django, flask), this is not intended to be used in a production environment. This rather is intended as a learning tool to understand how the server side components work (main focus being on servers and scalability). 
Everything from the server to the request handlers are written in python. It is quite hard to understand how various things work in big web frameworks, here things are simplified. We start from a simple HTTP server written over TCP and then work upon it till we reach an ngnix like model. Then we will add upon it a WSGI interface to give it a dynamic nature. 


##Steps taken by us
  1. Simple HTTP server
  2. Dynamic HTTP server - fork and exec (CGI)
  3. Event based HTTP server (epoll)
  4. Preforked server model (one active connection per worker)
  5. Worker model (workers have threads, one active connection per worker)
  6. Worker model with WSGI support for dynamisim 
  
All the code will be versioned in various folders. ```eg. /server/v1-simple-http/``` so it is easy for the reader to see what modifications have been made, and why a particular version is better than the previous one. 

### Authors
Deepak Karki
Aishwarya Kaliki 

### Contributors 
Deborah Digges
