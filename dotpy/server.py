import socket
from . import log
from threading import Thread

class Server(object):
	"""docstring for Server."""
	def __init__(self, host="127.0.0.1", port=0):
		super(Server, self).__init__()
		self.host = host
		self.port = port
		self.sock = None
		self.__running = False
		self.events = {
			"onmessage":None,
			"onconnected":None,
			"ondisconnected":None
		}

	def running(self):
		return self.__running

	def setaddr(self, host="127.0.0.1", port=0):
		""" set hostname and port """
		log(f"setting host to {host}, port to {port}")
		self.host, self.port = host, port

	def event(self, func):
		""" add event for server """
		def inner(self, func):
			name = func.__name__
			if name in self.events:
				log(f"adding event: {name}")
				self.events[name] = func
			else:
				# raise execption saying this shit doesnt exist
				raise Exception(f"this event '{name}' doesnt exist")
		return inner(self, func)

	def serve(self):
		Thread(target=self.__serve).start()

	def close(self):
		"shuts down server"
		if self.sock is not None: self.sock.close()
		return True

	# in functions
	def __serve(self):
		"""starts the server"""
		self.sock = socket.socket()
		self.sock.bind((self.host, self.port))
		self.sock.listen(10)
		self.__running = True

		while True:
			client, _ = self.sock.accept()
			Thread(target=self.events["onconnected"], args=(client,)).start()
