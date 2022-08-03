import shutil
import os


def hackman():
    gunicorn = shutil.which("gunicorn")
    if not gunicorn:
        raise ValueError("Missing gunicorn")

    os.execv(
        gunicorn,
        [
            "gunicorn",
            "--bind=unix:/tmp/hackman.sock",
            "--bind=127.0.0.1:8000",
            "--timeout",
            "120",
            "hackman.wsgi"
        ],
    )
