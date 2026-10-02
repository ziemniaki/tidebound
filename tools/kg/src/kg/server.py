"""Pinned local SurrealDB executable and foreground server lifecycle."""

import hashlib
import os
import platform
import secrets
import socket
import subprocess
import tarfile
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from urllib.request import urlopen

from filelock import FileLock

from . import storage
from .errors import DesignError

VERSION = "3.3.0"
ARCHIVES = {
    ("Darwin", "arm64"): (
        "darwin-arm64",
        "75e37adf5f9aacfa1308df71193b2d0e0727bc6532105541c083e71271cd7fc9",
    ),
    ("Darwin", "x86_64"): (
        "darwin-amd64",
        "c8e560d37c9f6f04b95f22791723122b5579f1fa5ac5102d6d82c36e38b72710",
    ),
    ("Linux", "x86_64"): (
        "linux-amd64",
        "44aeab565f7e7e39d2d0bf0583c8aae648babc91373c70b2658288d95bbbcd55",
    ),
    ("Linux", "aarch64"): (
        "linux-arm64",
        "f03356497f875057126641f06757671542e0a7b75f18fd13820c2dab29349d74",
    ),
}


def executable():
    """Install once from the official release, verifying the pinned archive digest."""
    target = ARCHIVES.get((platform.system(), platform.machine()))
    if target is None:
        raise DesignError("KG's local server currently supports macOS and Linux on ARM64/x64")
    name, digest = target
    cache = Path.home() / ".cache" / "kg" / f"surreal-{VERSION}-{name}"
    cache.mkdir(parents=True, exist_ok=True)
    binary = cache / "surreal"
    with FileLock(str(cache) + ".lock", timeout=120):
        if not binary.exists():
            url = f"https://github.com/surrealdb/surrealdb/releases/download/v{VERSION}/surreal-v{VERSION}.{name}.tgz"
            with urlopen(url, timeout=60) as response:
                archive = response.read()
            if hashlib.sha256(archive).hexdigest() != digest:
                raise DesignError("SurrealDB download checksum mismatch")
            with tempfile.TemporaryDirectory(dir=cache) as directory:
                package = Path(directory) / "server.tgz"
                package.write_bytes(archive)
                with tarfile.open(package) as bundle:
                    member = next(
                        m
                        for m in bundle.getmembers()
                        if m.name.lstrip("./") == "surreal" and m.isfile()
                    )
                    with bundle.extractfile(member) as source:
                        staged = Path(directory) / "surreal"
                        staged.write_bytes(source.read())
                staged.chmod(0o755)
                staged.replace(binary)
    return binary


def settings(path):
    config = Path(path) / "connection.json"
    if not config.is_file():
        raise DesignError(
            f"No local server configuration at {config}. Run kg setup, then kg serve."
        )
    value = storage.load(config)
    if (
        not isinstance(value, dict)
        or not isinstance(value.get("port"), int)
        or not 1 <= value["port"] <= 65535
    ):
        raise DesignError(f"Invalid server port in {config}")
    if not isinstance(value.get("password"), str) or not value["password"]:
        raise DesignError(f"Missing server password in {config}")
    return value


def setup(path, port=8000):
    path = Path(path).resolve()
    path.mkdir(parents=True, exist_ok=True)
    # Never interpret an old embedded store as a new server installation.
    config = path / "connection.json"
    if not config.exists() and any(path.iterdir()):
        raise DesignError(
            "Use a fresh server directory; migrate the old graph through its JSON export"
        )
    if not 1 <= port <= 65535:
        raise DesignError("Port must be between 1 and 65535")
    if not config.exists():
        with open(
            config, "x", encoding="utf-8", opener=lambda p, flags: os.open(p, flags, 0o600)
        ) as handle:
            handle.write(storage.canonical({"port": port, "password": secrets.token_urlsafe(24)}))
    value = settings(path)
    executable()
    return {"directory": str(path), "endpoint": endpoint(value), "version": VERSION}


def endpoint(config):
    return f"ws://127.0.0.1:{config['port']}"


def connection(path):
    value = settings(path)
    return {
        "endpoint": endpoint(value),
        "namespace": "kg",
        "database": "kg",
        "username": "kg",
        "password": value["password"],
    }


@contextmanager
def running(path):
    """Start exactly one foreground server; always stop the process we own."""
    path = Path(path).resolve()
    config = settings(path)
    binary = executable()
    with FileLock(str(path / "server.lock"), timeout=0):
        # Avoid starting on an occupied endpoint and accidentally using another graph.
        with socket.socket() as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            probe.bind(("127.0.0.1", config["port"]))
        env = {k: v for k, v in os.environ.items() if not k.startswith("SURREAL_")}
        env.update(SURREAL_USER="kg", SURREAL_PASS=config["password"])
        with (path / "server.log").open("ab") as log:
            process = subprocess.Popen(
                [
                    str(binary),
                    "start",
                    "--bind",
                    f"127.0.0.1:{config['port']}",
                    "--no-banner",
                    "--log",
                    "warn",
                    "surrealkv://" + str(path / "data"),
                ],
                env=env,
                stdout=log,
                stderr=log,
            )
            try:
                deadline = time.monotonic() + 20
                while True:
                    if process.poll() is not None:
                        raise DesignError(
                            f"SurrealDB stopped during startup; see {path / 'server.log'}"
                        )
                    try:
                        with urlopen(f"http://127.0.0.1:{config['port']}/health", timeout=1):
                            break
                    except OSError:
                        if time.monotonic() >= deadline:
                            raise DesignError(
                                f"SurrealDB startup timed out; see {path / 'server.log'}"
                            ) from None
                        time.sleep(0.1)
                yield process
            finally:
                if process.poll() is None:
                    process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
