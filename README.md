# Sockdot

### simplified tcp networking library
note: This is not a websocket
i'd write a little peice of introduction here, with a little bit of shit :D
documentation would be ready in a while

### Installation
```shell
pip install sockdot
```

### Usage

server.py

```python
from sockdot import Server
from sockdot.events import Event

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
	# print(f"error {exception} occured, message:", message)
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
import time, threading
from sockdot import Client
from sockdot.events import Event

clientevents = Event()
client = Client(host="rubbie-io", debug=True)

def start(connected):
	if connected:
		for i in range(10):
			client.send(str(i))
			time.sleep(4)
		client.close()

@clientevents.event
def on_data_recieved(data):
	print(f"got {data} from server")

@clientevents.event
def on_connected_changed(connected):
	threading.Thread(target=start, args=(connected,)).start()

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

```

## Adding authenthecation
create a file <b>".auth"</b>. the file contains keys and values of security parameters

```json
{
	"SECURITY_KEY" : "secret key",
	"WHITELIST": [],
	"BLACKLIST": [],
	"USE_WHITELIST": false
}
```

in server.py, make this change:
```python
# from file...
server = Server(debug=True, auth=".auth")

# from dictionary
server = Server(debug=True, auth={
	"SECURITY_KEY" : "secret key",
	"WHITELIST": [],
	"BLACKLIST": [],
	"USE_WHITELIST": False
})
```

in client.py, make this change:
```python
client.connect(authkey="secret key")
```
