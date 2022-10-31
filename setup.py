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

readme = ""
with open("README.md", encoding="utf-8") as f:
    readme = f.read()

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
    name="disnake",
    author="Rapptz, EQUENOS",
    url="https://github.com/DisnakeDev/disnake",
    project_urls={
        "Documentation": "https://docs.disnake.dev/en/latest",
        "Issue tracker": "https://github.com/DisnakeDev/disnake/issues",
    },
    version=version,
    packages=packages,
    license="MIT",
    description="A Python wrapper for the Discord API",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=requirements,
    extras_require=extras_require,
    python_requires=">=3.8.0",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)
