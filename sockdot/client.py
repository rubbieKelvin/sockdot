import os
import base64
import socket
import logging
import threading

from . import response
from . import events

class Client:
	_LOGS_FILE = "client.log"
	_EVENTS = {
		"on_data_recieved": events.void,	# param: data
		"on_connected_changed": events.void,	# param: connected
		"on_error": events.void,				# param: exception, message
		"on_host_changed": events.void,		# param: host
		"on_port_changed": events.void,		# param: port
		"on_handshake_started": events.void,	# no param
		"on_handshake_ended": events.void	# param: result
	}
	def __init__(self, port=80, host="0.0.0.0", debug=False, event={}):
		super(Client, self).__init__()
		self.connected = False
		self.sock = None
		self.host = host
		self.port = port
		self.debug = debug

		# Initialize log file format.
		logging.basicConfig(
			filename=Client._LOGS_FILE,
			filemode='w',
			format='%(levelname)s: %(asctime)s\t%(message)s',
			level=logging.DEBUG if self.debug else logging.INFO
		)

		# get events
		self.events = Client._EVENTS.copy()
		self.events.update(event.get() if type(event)==events.Event else event.copy())

	def updateevent(self, event):
		self.events.update(event.get() if type(event)==events.Event else event.copy())

	def sethost(self, host):
		self.host = host
		self.events["on_host_changed"](host)

	def setport(self, port):
		self.port = port
		self.events["on_port_changed"](port)

	def connect(self, authkey="0"):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		threading.Thread(target=self.connect_, args=(authkey,)).start()

	def connect_(self, authkey):
		try:
			self.sock.connect((self.host, self.port))
			logging.info("initial connection started")
			self.events["on_handshake_started"]()
			try:
				self.handshake(authkey)
			except (ConnectionAbortedError, ConnectionResetError) as e:
				err_msg = "server shutdown during handshake"
				self.events["on_error"](e, err_msg)
				logging.error(err_msg)
				self.close()
		except ConnectionRefusedError as e:
			err_msg = "no connection could be made because host doesnt exist"
			self.events["on_error"](e, err_msg)
			self.close()

	def handshake(self, authkey):
		self.send(authkey)
		logging.info("authkey sent")
		res = self.recv()
		self.events["on_handshake_ended"](res==response.HANDSHAKE_SUCCESSFUL)
		if res == response.HANDSHAKE_SUCCESSFUL:
			logging.info("handshake successful")
			self.connected = True
			self.events["on_connected_changed"](self.connected)
			threading.Thread(target=self.listen).start()
		elif res == response.HANDSHAKE_UNSUCCESSFUL:
			logging.error("handshake unsuccessful")
			self.close()

	def listen(self):
		while self.connected:
			try:
				data = self.recv()
				print("recieved", data)
				self.events["on_data_recieved"](data)
				logging.info("recieved data: "+data)
			except (ConnectionResetError, ConnectionAbortedError) as e:
				msg = "server shutdown unexpectedly"
				self.events["on_error"](e, msg)
				logging.error(msg)
				self.close()

	def send(self, data):
		if data:
			data = bytes(str(data), "utf8") if type(data)!=bytes else data
			res = self.sock.send(data)
			return res
		return 0

	def recv(self):
		return self.sock.recv(2048).decode("utf8")

	def close(self):
		if self.sock is not None: self.sock.close()
		self.sock = None
		self.connected = False
		self.events["on_connected_changed"](self.connected)
