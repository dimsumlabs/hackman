# type: ignore
import subprocess
import typing


p: typing.Optional[subprocess.Popen] = None


def pytest_sessionstart(session):
    global p
    p = subprocess.Popen(["redis-server", "--save", "", "--port", "31337"])


def pytest_sessionfinish(session, exitstatus):
    global p
    if not p:  # Make type checker happy
        raise ValueError("Process was None")
    p.kill()
