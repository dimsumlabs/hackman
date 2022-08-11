import os.path
import sys
import os


def hackman():
    os.execv(
        os.path.join(os.path.dirname(sys.executable), "gunicorn"),
        [
            "gunicorn",
            "--workers",
            "1",
            "hackman.wsgi",
        ],
    )
