from __future__ import annotations

import functools
import re
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Optional, TypeVar

import nox

nox.options.error_on_external_run = True
nox.options.reuse_existing_virtualenvs = True
nox.options.sessions = [
    "lint",
    "pyright",
    "tests",
]
nox.needs_version = ">=2022.1.7"


REQUIREMENTS = {
    ".": "requirements.txt",
}
for path in Path("requirements").iterdir():
    if match := re.fullmatch("requirements_(.+).txt", path.name):
        REQUIREMENTS[match.group(1)] = str(path)


if TYPE_CHECKING:
    from typing_extensions import Concatenate, ParamSpec

    P = ParamSpec("P")
    T = TypeVar("T")

    NoxSessionFunc = Callable[Concatenate[nox.Session, P], T]


def depends(
    *deps: str, update: bool = True
) -> Callable[[NoxSessionFunc[P, T]], NoxSessionFunc[P, T]]:
    def decorator(f: NoxSessionFunc[P, T]) -> NoxSessionFunc[P, T]:
        @functools.wraps(f)
        def wrapper(session: nox.Session, *args: P.args, **kwargs: P.kwargs) -> T:
            install(session, *deps, update=update)
            return f(session, *args, **kwargs)

        return wrapper

    return decorator


def install(session: nox.Session, *deps: str, update: bool = True, run: bool = False) -> None:
    install_args = ["-U"] if update else []
    for d in (".", *deps):
        install_args.extend(["-r", REQUIREMENTS[d]])

    if run:
        session.run("python", "-m", "pip", "install", *install_args)
    else:
        session.install(*install_args)


@nox.session()
@depends("docs")
def docs(session: nox.Session):
    """Build and generate the documentation.

    If running locally, will build automatic reloading docs.
    If running in CI, will build a production version of the documentation.
    """
    with session.chdir("docs"):
        args = ["-b", "html", "-j", "auto", "-n", ".", "_build/html"]
        if session.interactive:
            session.run(
                "sphinx-autobuild",
                "--ignore",
                "_build",
                "--watch",
                "../disnake",
                "--port",
                "8009",
                *args,
            )
        else:
            session.run(
                "sphinx-build",
                "-aE",
                *args,
            )


@nox.session()
@depends("dev")
def lint(session: nox.Session):
    """Check all files for linting errors"""
    session.run("pre-commit", "run", "--all-files")


@nox.session()
@depends("dev")
def slotscheck(session: nox.Session):
    """Run slotscheck."""
    session.run("python", "-m", "slotscheck", "--verbose", "-m", "disnake")


@nox.session()
@depends("dev", "docs", "speed", "voice")
def pyright(session: nox.Session):
    """Run pyright."""
    env = {
        "PYRIGHT_PYTHON_IGNORE_WARNINGS": "1",
    }
    try:
        session.run("python", "-m", "pyright", *session.posargs, env=env)
    except KeyboardInterrupt:
        pass


@nox.session()
@nox.parametrize("extras", [None, "speed", "voice"])
@depends("dev")
def tests(session: nox.Session, extras: Optional[str]):
    """Run tests."""
    if extras:
        install(session, extras)

    # todo: only run tests that depend on the different dependencies
    session.run("pytest", "-v", "--cov", "--cov-report=term", "--cov-append", "--cov-context=test")
    session.notify("coverage", session.posargs)


@nox.session()
@depends("dev")
def coverage(session: nox.Session):
    """Display coverage information from the tests."""
    if "html" in session.posargs or "serve" in session.posargs:
        session.run("coverage", "html", "--show-contexts")
    if "serve" in session.posargs:
        session.run(
            "python", "-m", "http.server", "8009", "--directory", "htmlcov", "--bind", "127.0.0.1"
        )
    if "erase" in session.posargs:
        session.run("coverage", "erase")


@nox.session(python=False)
def setup(session: nox.Session):
    """Set up the local environment."""
    session.log("Installing dependencies to the global environment.")

    if session.posargs:
        deps = list(session.posargs)
    else:
        deps = list(REQUIREMENTS.keys())

    if "." not in deps:
        deps.insert(0, ".")  # index doesn't really matter

    install(session, *deps, run=True)

    if "lint" in deps:
        session.run("pre-commit", "install", "--install-hooks")
