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
from abc import ABC, abstractmethod
from http.server import BaseHTTPRequestHandler
from pathlib import Path


class Request(ABC):
    @abstractmethod
    def get(self, handler: BaseHTTPRequestHandler) -> None:
        pass


class ContentGet(Request):
    def __init__(self, content: str) -> None:
        self.__content = content

    def get(self, handler: BaseHTTPRequestHandler) -> None:
        handler.send_response(200)
        handler.send_header("Content-type", "text/html")
        handler.end_headers()
        handler.wfile.write(self.__content.encode())


class FileContentGet(Request):
    def __init__(self, filename: str) -> None:
        self.__filename = filename

    def get(self, handler: BaseHTTPRequestHandler) -> None:
        handler.send_response(200)
        handler.send_header("Content-type", "text/html; charset=utf8")
        handler.end_headers()
        buffer = Path(self.__filename).read_bytes()
        handler.wfile.write(buffer)


class Fail(Request):
    def __init__(self, request: Request, retries: int) -> None:
        self.__origin = request
        self.__retries = retries

    def get(self, handler: BaseHTTPRequestHandler) -> None:
        if self.__retries > 0:
            handler.connection.close()
            self.__retries -= 1
        else:
            self.__origin.get(handler)
