from __future__ import annotations

import functools
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Callable, List, TypeVar

import nox

if TYPE_CHECKING:
    from typing_extensions import Concatenate, ParamSpec

    P = ParamSpec("P")
    T = TypeVar("T")

    NoxSessionFunc = Callable[Concatenate[nox.Session, P], T]


nox.options.error_on_external_run = True
nox.options.reuse_existing_virtualenvs = True
nox.options.sessions = [
    "lint",
    "check-manifest",
    "slotscheck",
    "pyright",
    "test",
]
nox.needs_version = ">=2022.1.7"


# used to reset cached coverage data once for the first test run only
reset_coverage = True


REQUIREMENTS = {
    ".": "requirements.txt",
}
for path in Path("requirements").iterdir():
    if match := re.fullmatch("requirements_(.+).txt", path.name):
        REQUIREMENTS[match.group(1)] = str(path)


def depends(
    *deps: str,
    install_cwd: bool = False,
    update: bool = True,
) -> Callable[[NoxSessionFunc[P, T]], NoxSessionFunc[P, T]]:
    """A session decorator that invokes :func:`.install` with the given parameters before running the session."""

    def decorator(f: NoxSessionFunc[P, T]) -> NoxSessionFunc[P, T]:
        @functools.wraps(f)
        def wrapper(session: nox.Session, *args: P.args, **kwargs: P.kwargs) -> T:
            install(session, *deps, update=update, install_cwd=install_cwd)
            return f(session, *args, **kwargs)

        return wrapper

    return decorator


def install(
    session: nox.Session,
    *deps: str,
    run: bool = False,
    install_cwd: bool = False,
    update: bool = True,
) -> None:
    """
    Installs dependencies in a session.
    Dependencies from the main ``requirements.txt`` will always be installed.

    Parameters
    ----------
    *deps: :class:`str`
        Dependency group names, e.g. ``dev`` for ``requirements_dev.txt``.
    run: :class:`bool`
        Whether to use :func:`nox.Session.run` instead of :func:`nox.Session.install`,
        useful to avoid warnings when running in the global python environment.
    install_cwd: :class:`bool`
        Whether the main package should be installed (in editable mode, i.e. ``-e .``).
    update: :class:`bool`
        Whether packages should be updated (i.e. ``-U``). Defaults to ``True``.
    """

    install_args = []

    if update:
        install_args.append("-U")
    if install_cwd:
        install_args.extend(["-e", "."])

    for d in dict.fromkeys((".", *deps)):  # deduplicate
        install_args.extend(["-r", REQUIREMENTS[d]])

    if run:
        session.run("python", "-m", "pip", "install", *install_args)
    else:
        session.install(*install_args)


def is_venv() -> bool:
    # https://stackoverflow.com/a/42580137/5080607
    return (
        # virtualenv < v20
        hasattr(sys, "real_prefix")
        # virtualenv >= v20, others
        or sys.base_prefix != sys.prefix
    )


@nox.session()
@depends("docs")
def docs(session: nox.Session):
    """Build and generate the documentation.

    If running locally, will build automatic reloading docs.
    If running in CI, will build a production version of the documentation.
    """
    with session.chdir("docs"):
        args = ["-b", "html", "-n", ".", "_build/html", *session.posargs]
        if session.interactive:
            session.run(
                "sphinx-autobuild",
                "--ignore",
                "_build",
                "--watch",
                "../disnake",
                "--watch",
                "../changelog",
                "--port",
                "8009",
                "-j",
                "auto",
                *args,
            )
        else:
            session.run(
                "sphinx-build",
                "-aE",
                *args,
            )


@nox.session(python=False)
def lint(session: nox.Session):
    """Check all files for linting errors"""
    session.run("pre-commit", "run", "--all-files", *session.posargs)


@nox.session(name="check-manifest")
@depends("tools")
def check_manifest(session: nox.Session):
    """Run check-manifest."""
    session.run("check-manifest", "-v", "--no-build-isolation")


@nox.session()
@depends("dev")
def slotscheck(session: nox.Session):
    """Run slotscheck."""
    session.run("python", "-m", "slotscheck", "--verbose", "-m", "disnake")


@nox.session()
@depends("dev", "docs", "speed", "voice", install_cwd=True)
def pyright(session: nox.Session):
    """Run pyright."""
    env = {
        "PYRIGHT_PYTHON_IGNORE_WARNINGS": "1",
    }
    try:
        session.run("python", "-m", "pyright", *session.posargs, env=env)
    except KeyboardInterrupt:
        pass


@nox.session(python=["3.8", "3.9", "3.10"])
@nox.parametrize(
    "extras",
    [
        [],
        # NOTE: disabled while there are no tests that would require these dependencies
        # ["speed"],
        # ["voice"],
    ],
)
def test(session: nox.Session, extras: List[str]):
    """Run tests."""
    install(session, "dev", *extras)

    pytest_args = ["--cov", "--cov-context=test"]
    global reset_coverage
    if reset_coverage:
        # don't use `--cov-append` for first run
        reset_coverage = False
    else:
        # use `--cov-append` in all subsequent runs
        pytest_args.append("--cov-append")

    # TODO: only run tests that depend on the different dependencies
    session.run(
        "pytest",
        *pytest_args,
        *session.posargs,
    )


@nox.session()
@depends("dev")
def coverage(session: nox.Session):
    """Display coverage information from the tests."""
    if "html" in session.posargs or "serve" in session.posargs:
        session.run("coverage", "html", "--show-contexts")
    if "serve" in session.posargs:
        session.run(
            "python", "-m", "http.server", "8012", "--directory", "htmlcov", "--bind", "127.0.0.1"
        )
    if "erase" in session.posargs:
        session.run("coverage", "erase")


@nox.session(python=False)
def setup(session: nox.Session):
    """Set up the external environment."""
    if session.interactive and not is_venv():
        confirm = input(
            "It looks like you are about to install the dependencies into your *global* python environment."
            " This may overwrite other versions of the dependencies that you already have installed, including disnake itself."
            " Consider using a virtual environment (virtualenv/venv) instead. Continue anyway? [y/N]"
        )
        if confirm.lower() != "y":
            session.error("Cancelled")

    session.log("Installing dependencies to the external environment.")

    if session.posargs:
        deps = list(session.posargs)
    else:
        deps = list(REQUIREMENTS.keys())

    if "." not in deps:
        deps.insert(0, ".")  # index doesn't really matter

    install(session, *deps, run=True, install_cwd=True)

    if session.interactive and "dev" in deps:
        session.run("pre-commit", "install", "--install-hooks")
