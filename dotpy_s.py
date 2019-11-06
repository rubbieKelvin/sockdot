import dotpy
import os, sys
from  dotpy import server

dotpy.DEBUG = True

server = server.Server()
server.setaddr(host=dotpy.HOST, port=90)
server.serve()

@server.event
def onmessage(self, message):
	pass

@server.event
def connected(self, client):
	pass

@server.event
def disconnected(self, client):
	pass
