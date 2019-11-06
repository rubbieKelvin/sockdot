import socket

HOST = socket.gethostname()
DEBUG = False

def log(*args, **kwargs):
	if DEBUG: print(*args, **kwargs)
