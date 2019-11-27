# DotPy

### simplified tcp networking library
note: This is not a websocket
i'd write a little peice of introduction here, with a little bit of shit :D
documentation would be ready in a while

### Installation
```shell
pip install dotpy
```

### Usage

server.py

```python
from dotpy import Server
from dotpy.events import Event

serverevents = Event()
server = Server(debug=True)

@serverevents.event
def on_data_recieved(client, data):
	print("recieved:", data)
	server.send(client, f"you said {data}")

@serverevents.event
def on_connection_open(client):
	print(f"client {client} joined")

@serverevents.event
def on_connection_close(client):
	print(client, "closed connection")

@serverevents.event
def on_server_destruct():
	print("server shutdown")

@serverevents.event
def on_error(exception, message):
	pass

@serverevents.event
def on_port_changed(port):
	print("server changed port to", port)

@serverevents.event
def on_running_changed(running):
	print("server is running" if running else "server is not running")

server.updateevent(serverevents)
server.run()

```

client.py

```python
import time
from dotpy import Client
from dotpy.events import Event

clientevents = Event()
client = Client(host="localhost", debug=True)

@clientevents.event
def on_data_recieved(data):
	print(f"got {data} from server")

@clientevents.event
def on_connected_changed(connected):
	pass

@clientevents.event
def on_error(exception, message):
	print(f"error {exception} occured, message:", message)

@clientevents.event
def on_host_changed(host):
	pass

@clientevents.event
def on_port_changed(port):
	pass

@clientevents.event
def on_handshake_started():
	pass

@clientevents.event
def on_handshake_ended(result):
	pass

client.updateevent(clientevents)
client.connect()

# hold on until client gets connected to server
while True:
	if client.connected:
		break

# send i for i in range 10
for i in range(10):
	client.send(str(i))
	time.sleep(4)
client.close()

```
