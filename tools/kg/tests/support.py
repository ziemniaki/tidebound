"""Isolated real server fixtures shared by the KG and game snapshot suites."""

import socket
from contextlib import contextmanager

from kg import server


@contextmanager
def local_server(path):
    if not (path / "connection.json").exists():
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        server.setup(path, port)
    with server.running(path):
        yield path
