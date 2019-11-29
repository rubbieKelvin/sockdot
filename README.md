# Sockdot

### simplified tcp networking library
note: This is <b>not a websocket.</b>
<br>

sockdot allows you to create server/client applications without having to use web-standard protocols in your application. the library is a threaded tcp socket and allows for events to be used, making it easy to inpliment in server/client application. i created this library to meet my needs in a Lan software project, so 't could be of use to someone else :).

### Installation
```shell
pip install sockdot
```

Installing from source.
```shell
git clone https://github.com/rubbiekelvin/sockdot.git
cd sockdot
python setup.py sdist bdist_wheel
pip install dist\sockdot-1.0.1-py3-none-any.whl
```

### Usage

server.py</br>
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
<small>the server's runs on the machine's host name</small>
```python
from sockdot import host
print(host())
# outputs ["host_name", "host_ip"]
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
create a file <b>".auth"</b>, could be anything you want, but in my case, i named it ".auth". the file contains keys and values of security parameters in json format.


```json
{
	"SECURITY_KEY" : "secret key",
	"WHITELIST": [],
	"BLACKLIST": [],
	"USE_WHITELIST": false
}
```

in server.py, make this change:<br>
note that it is also possible for auth settings to be in a python dictionary, use could use any one you want. the <span style="color: #26c6da;">auth</span> keyword argument can be a <span style="color: #ffa000;">str</span> (filename) type or <span style="color: #ffa000;">dict</span> (auth dictionary).
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
