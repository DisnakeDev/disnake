# SPDX-License-Identifier: MIT

import re

from setuptools import setup


def read_requirements(path: str):
    with open(path, "r", encoding="utf-8") as f:
        lines = (x.strip() for x in f.read().splitlines())
        return [x for x in lines if x and not x.startswith("#")]


requirements = read_requirements("requirements.txt")

version = ""
with open("disnake/__init__.py", encoding="utf-8") as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)  # type: ignore

if not version:
    raise RuntimeError("version is not set")

if version.endswith(("a", "b", "rc")):
    # append version identifier based on commit count
    try:
        import subprocess  # noqa: S404

        p = subprocess.Popen(  # noqa: S603,S607
            ["git", "rev-list", "--count", "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        out, err = p.communicate()
        if out:
            version += out.decode("utf-8").strip()
        p = subprocess.Popen(  # noqa: S603,S607
            ["git", "rev-parse", "--short", "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        out, err = p.communicate()
        if out:
            version += "+g" + out.decode("utf-8").strip()
    except Exception:
        pass

extras_require = {
    "voice": read_requirements("requirements/requirements_voice.txt"),
    "docs": read_requirements("requirements/requirements_docs.txt"),
    "speed": read_requirements("requirements/requirements_speed.txt"),
    "discord": ["discord-disnake"],
}

packages = [
    "disnake",
    "disnake.bin",
    "disnake.types",
    "disnake.ui",
    "disnake.ui.select",
    "disnake.webhook",
    "disnake.interactions",
    "disnake.ext.commands",
    "disnake.ext.tasks",
    "disnake.ext.mypy_plugin",
]

setup(
    version=version,
    packages=packages,
    include_package_data=True,
    install_requires=requirements,
    extras_require=extras_require,
)
