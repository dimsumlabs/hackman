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
            "--workers",
            "1",
            "hackman.wsgi",
        ],
    )
