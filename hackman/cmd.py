import os.path
import shutil
import sys
import os


def hackman() -> None:
    # Take gunicorn from venv if using venv based workflow
    bin = os.path.join(os.path.dirname(sys.executable), "gunicorn")

    # Take from global env
    if not os.path.exists(bin):
        bin = shutil.which("gunicorn")

    if not bin:
        raise RuntimeError("Could not find gunicorn executable")

    os.execve(
        bin,
        [
            "gunicorn",
            "--workers",
            "1",
            "-k",
            "gevent",
            "hackman.wsgi",
        ]
        + sys.argv[1:],
        {
            # Note: Nix environments created with `withPackages` & such do not set PYTHONPATH
            # and the venv-like Nix store path gets "lost" in execution.
            # Recreate the PYTHONPATH from sys.path to inherit across exec's.
            "PYTHONPATH": ":".join(sys.path),
        }
    )
