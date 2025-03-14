# The MIT License (MIT)
#
# Copyright (C) 2025 Fabrício Barros Cabral
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import http.client
import ssl
from pathlib import Path

from fake_https_server.request import ContentGet, Fail, FileContentGet
from fake_https_server.server import Daemon, FakeHttpServer, FakeHttpsServer


def test_file_content_get() -> None:
    ca_file = Path(__file__).parent.parent / "certificates" / "ca.crt"
    content_file = Path(__file__).parent / "contents" / "hello-world.txt"
    server = Daemon(FakeHttpsServer(FileContentGet(content_file)))
    server.start()
    client = http.client.HTTPSConnection(
        "localhost", 8443, context=ssl.create_default_context(cafile=ca_file)
    )
    client.request("GET", "/")
    response = client.getresponse()
    content = response.read().decode()
    server.stop()
    assert content == "Hello World!\n"


def test_large_file() -> None:
    ca_file = Path(__file__).parent.parent / "certificates" / "ca.crt"
    content_file = Path(__file__).parent / "contents" / "large.html"
    content = Path(content_file).read_text(encoding="utf-8")
    server = Daemon(FakeHttpsServer(FileContentGet(content_file)))
    server.start()
    client = http.client.HTTPSConnection(
        "localhost", 8443, context=ssl.create_default_context(cafile=ca_file)
    )
    client.request("GET", "/")
    response = client.getresponse()
    html = response.read().decode()
    server.stop()
    assert content == html


def test_fail() -> None:
    retries = 1
    msg = "It works!"
    server = Daemon(FakeHttpServer(Fail(ContentGet(msg), retries)))
    server.start()
    try:
        client = http.client.HTTPConnection("localhost", 8080)
        client.request("GET", "/")
        response = client.getresponse()
    except Exception:
        client = http.client.HTTPConnection("localhost", 8080)
        client.request("GET", "/")
        response = client.getresponse()
    assert response.read().decode() == msg
    server.stop()
