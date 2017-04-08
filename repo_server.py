#!/usr/bin/env python
#####################################################################
# simple web server to run a local repository
# ./repo_server.py
#####################################################################
import SimpleHTTPServer
import SocketServer

PORT = 8181
LISTEN = '127.0.0.1'

Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

httpd = SocketServer.TCPServer((LISTEN,PORT), Handler)

print 'Server starting. URL: http://%s:%s' % (LISTEN, PORT)
httpd.serve_forever()

