class Event:
	def __init__(self):
		self.events = {}

	def event(self, func):
		self.events[func.__name__] = func

	def get(self):
		return self.events.copy()

def void(*args, **kwargs):
	pass
