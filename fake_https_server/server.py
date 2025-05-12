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
import ssl
import sys
import threading
from abc import ABC, abstractmethod
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

from random_port.pool import TcpRandomPort

from fake_https_server.request import Request


class Server(ABC):
    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def host(self) -> str:
        pass

    @abstractmethod
    def port(self) -> int:
        pass

    @abstractmethod
    def protocol(self) -> str:
        pass


class HandlerWrapper(BaseHTTPRequestHandler):
    def __init__(
        self, request: Request, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> None:
        self.__request = request
        super().__init__(*args, **kwargs)

    def log_message(self, fmt: str, *args: Any) -> None:
        pass

    def do_GET(self) -> None:
        self.__request.get(self)


class FakeHttpServer(Server):
    def __init__(
        self,
        request: Request,
        host: str = "localhost",
        port: TcpRandomPort | int = TcpRandomPort(),
    ) -> None:
        self.__host = host
        self.__port = port.value()

        def __handler_wrapper(
            *args: tuple[Any, ...], **kwargs: dict[str, Any]
        ) -> BaseHTTPRequestHandler:
            return HandlerWrapper(request, *args, **kwargs)

        self.__httpd = HTTPServer((self.__host, self.__port), __handler_wrapper)

    def start(self) -> None:
        try:
            self.__httpd.serve_forever()
        except Exception:
            self.stop()

    def stop(self) -> None:
        self.__httpd.shutdown()
        self.__httpd.server_close()

    def host(self) -> str:
        return self.__host

    def port(self) -> int:
        return self.__port

    def protocol(self) -> str:
        return "http"


class FakeHttpsServer(Server):
    def __init__(
        self,
        request: Request,
        host: str = "localhost",
        port: TcpRandomPort | int = TcpRandomPort(),
        *,
        cert_file: Path | str = "certificates/server.crt",
        key_file: Path | str = "certificates/server.key",
        ca_file: Path | str = "certificates/ca.crt",
    ) -> None:
        self.__host = host
        self.__port = port.value()

        def __handler_wrapper(
            *args: tuple[Any, ...], **kwargs: dict[str, Any]
        ) -> BaseHTTPRequestHandler:
            return HandlerWrapper(request, *args, **kwargs)

        cert_file = str(Path(cert_file).resolve())
        key_file = str(Path(key_file).resolve())
        ca_file = str(Path(ca_file).resolve())
        self.__httpsd = HTTPServer(
            (self.__host, self.__port), __handler_wrapper
        )
        sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        sslctx.load_cert_chain(certfile=cert_file, keyfile=key_file)
        sslctx.load_verify_locations(ca_file)
        self.__httpsd.socket = sslctx.wrap_socket(
            self.__httpsd.socket, server_side=True
        )

    def start(self) -> None:
        try:
            self.__httpsd.serve_forever()
        except Exception:
            self.stop()

    def stop(self) -> None:
        self.__httpsd.shutdown()
        self.__httpsd.server_close()

    def host(self) -> str:
        return self.__host

    def port(self) -> int:
        return self.__port

    def protocol(self) -> str:
        return "https"


class Logged(Server):
    def __init__(self, server: Server) -> None:
        self.__origin = server

    def start(self) -> None:
        host = self.__origin.host()
        port = self.__origin.port()
        print(
            f"Starting {self.protocol().upper()} server at "
            f"https://{host}:{port}... ",
            end="",
            flush=True,
            file=sys.stderr,
        )
        self.__origin.start()
        print("done.", flush=True, file=sys.stderr)

    def stop(self) -> None:
        print(
            f"Stopping {self.protocol().upper()} server... ",
            end="",
            flush=True,
            file=sys.stderr,
        )
        self.__origin.stop()
        print("done.", flush=True, file=sys.stderr)

    def host(self) -> str:
        return self.__origin.host()

    def port(self) -> int:
        return self.__origin.port()

    def protocol(self) -> str:
        return self.__origin.protocol()


class Daemon(Server):
    def __init__(self, server: Server) -> None:
        self.__origin = server
        self.__thread = threading.Thread(target=self.__origin.start)
        self.__thread.daemon = True

    def start(self) -> None:
        self.__thread.start()

    def stop(self) -> None:
        self.__origin.stop()
        self.__thread.join()

    def host(self) -> str:
        return self.__origin.host()

    def port(self) -> int:
        return self.__origin.port()

    def protocol(self) -> str:
        return self.__origin.protocol()
