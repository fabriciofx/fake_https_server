# Fake Https Server

## Introduction

Fake Https Server is a package to create auto assigned HTTPS and HTTP servers to
use with tests. Useful to tests web scrapers and https or https clients.

## How create auto assigned certiticates

Follow `docs/receita-servidor-cliente-ssl.md` recipe.

## How to use

Install it using `pip` command:

```bash
pip install fake_https_server
```

in your project folder.

## Usage

First, generate the server and ca certificates. To do it, follow the recipe.
Then, you can use HTTP or HTTPS server as follow:

### Fake HTTP Server

```python
# Message to be sent
msg = "It works"
# Create the fake HTTP server. By default the HTTP server will listen at
# localhost, port 8080
server = Daemon(FakeHttpServer(ContentGet(msg)))
# Start the server
server.start()
# Make a http client connection to the server.
client = http.client.HTTPConnection("localhost", 8080)
client.request("GET", "/")
# Get the server response
response = client.getresponse()
content = response.read().decode()
# Stop the fake http server
server.stop()
```

### Fake HTTPS Server

```python
# Path to ca certificate file (the https client needs it)
ca_file = Path(__file__).parent.parent / "certificates" / "ca.crt"
# Message to be sent
msg = "It works!"
# Create the fake HTTPS server. By default the HTTPS server will listen at
# localhost, port 8443
server = Daemon(FakeHttpsServer(ContentGet(msg)))
# Start the server
server.start()
# Make a https client connection to the server
client = http.client.HTTPSConnection(
    "localhost",
    8443,
    context=ssl.create_default_context(cafile=ca_file)
)
client.request("GET", "/")
# Get the server response
response = client.getresponse()
content = response.read().decode()
# Stop the fake http server
server.stop()
```

## License

The MIT License (MIT)

Copyright (C) 2025 Fabrício Barros Cabral

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
