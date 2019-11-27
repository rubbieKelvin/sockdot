import os
import json
import base64
import socket
import logging
import threading

from . import response
from . import events

class Server:
	_LOGS_FILE = "server.log"
	_EVENTS = {
		"on_data_recieved": events.void,	# param: client, data
		"on_connection_open": events.void,	# param: client
		"on_connection_close": events.void,	# param: client
		"on_server_destruct": events.void,	# no param
		"on_error": events.void,			# param: exception, message
		"on_port_changed": events.void,		# param: port
		"on_running_changed": events.void	# param: running
	}
	def __init__(self, port=80, debug=False, auth=None, event={}):
		super(Server, self).__init__()
		self.sock = None
		self.port = port
		self.clients = set()
		self.debug = debug

		# extract auth file
		self.auth = {
			"SECURITY_KEY": "",
			"WHITELIST": [],
			"BLACKLIST": [],
			"USE_WHITELIST": False
		}
		if auth is None:
			self.auth = auth
		else:
			with open(auth) as file:
				self.auth.update(json.load(file))

		# Initialize log file format.
		logging.basicConfig(
			filename=Server._LOGS_FILE,
			filemode='w',
			format='%(levelname)s: %(asctime)s\t%(message)s',
			level=logging.DEBUG if self.debug else logging.INFO
		)

		# get events
		self.events = Server._EVENTS.copy()
		self.events.update(event.get() if type(event)==events.Event else event.copy())

	def updateevent(self, event):
		self.events.update(event.get() if type(event)==events.Event else event.copy())

	@property
	def host(self):
		return socket.gethostname()

	@property
	def alive(self):
		return self.sock is not None

	def setport(self, port):
		self.port = port
		self.events["on_port_changed"](port)

	def run(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.events["on_running_changed"](self.alive)
		self.sock.bind((self.host, self.port))
		self.sock.listen(5)
		threading.Thread(target=self.run_).start()

	def run_(self):
		logging.info("server started!")
		while self.alive:
			try:
				logging.info("waiting for connection")
				client, addr = self.sock.accept()
				logging.info(f"client {addr} joined")
				self.events["on_connection_open"](client)
				threading.Thread(target=self.handshake, args=(client, addr)).start()
			except OSError as e:
				err_msg = "error occured during server shutdown"
				self.events["on_error"](e, err_msg)
				self.events["on_server_destruct"]()
				logging.error(err_msg)
				break

	def handshake(self, client, addr):
		auth = self.recv(client)
		rep = self.authenticate(auth, addr)
		logging.info(f"handshake response from client {addr[0]}: {rep}")
		if rep:
			# handle client
			logging.info(f"handshake with client {addr} successfull")
			self.clients.add(client)
			self.send(client, response.HANDSHAKE_SUCCESSFUL)
			threading.Thread(target=self.manageclient, args=(client,)).start()
		else:
			# dump client
			logging.error(f"handshake with client {addr} unsuccessfull")
			self.send(client, response.HANDSHAKE_UNSUCCESSFUL)
			client.close()

	def authenticate(self, data, addr):
		res = False
		if self.auth is not None:
			# check security key
			if self.auth["SECURITY_KEY"]:
				if data == self.auth["SECURITY_KEY"]:
					res = True
				else:
					return False
			# check in whitelist
			if not self.auth["USE_WHITELIST"]:
				res = True
			else:
				if addr[0] in self.auth["WHITELIST"]:
					res = True
				else:
					return False
			# check in blacklist
			if addr in self.auth["BLACKLIST"]:
				return False
			else:
				res = True
		else:
			return True
		return res

	def recv(self, client):
		return client.recv(2048).decode("utf8")

	def send(self, client, data):
		client.send(bytes(data, "utf8"))

	def broadcast(self, data):
		for client in self.clients:
			self.send(client, data)

	def manageclient(self, client):
		while self.alive:
			try:
				data = self.recv(client)
				self.events["on_data_recieved"](client, data)
			except ConnectionResetError:
				# client closed connection
				self.events["on_connection_close"](client)
				logging.info("client {client} left")
				self.clients.remove(client)
				break

	def kill(self):
		logging.info("server shutdown")
		if self.alive: self.sock.close()
		self.sock = None
		self.events["on_running_changed"](self.alive)
		self.client = set()
