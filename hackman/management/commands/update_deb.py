from django.core.management.base import BaseCommand
import subprocess
import requests
import tempfile
import os.path
import os
import re
import typing

from hackman.settings import DB_DIR


# Deb package auto updater, this runs in a oneshot systemd unit on a timer on the pi.


GITHUB_URL = "https://api.github.com/repos/dimsumlabs/hackman/releases/latest"
ARCH = "armhf"


def download_file(url: str, dst: str) -> None:
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(dst, "wb") as f:
            for c in r.iter_content(chunk_size=8192):
                f.write(c)


class Command(BaseCommand):
    def handle(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        r = requests.get(GITHUB_URL)

        if not r.ok:
            raise ValueError(f"Request returned {r.status_code}")

        resp = r.json()

        try:
            os.mkdir(DB_DIR)
        except FileExistsError:
            pass

        # Get current rev
        try:
            with open(os.path.join(DB_DIR, "deb-tag-name")) as f:
                tag_name = f.read()
        except FileNotFoundError:
            tag_name = ""

        # Same rev?
        if resp["tag_name"] == tag_name:
            return

        # Find correct deb asset
        for asset in resp["assets"]:
            if re.match(r"hackman_.+%s\.deb" % ARCH, asset["name"]):
                deb_url = asset["browser_download_url"]
                break
        else:
            raise ValueError("No deb found in latest release")

        with tempfile.TemporaryDirectory() as tmpdir:
            deb = os.path.join(tmpdir, "hackman.deb")

            download_file(deb_url, deb)

            # Update package
            subprocess.run(
                [
                    "apt",
                    "install",
                    "-y",
                    "-f",
                    deb,
                ],
                check=True,
            )

        # Write current rev file
        with open(os.path.join(DB_DIR, "deb-tag-name"), "w") as f:
            f.write(resp["tag_name"])
