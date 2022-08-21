# SPDX-License-Identifier: MIT

from __future__ import annotations

import functools
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
    "slotscheck",
    "pyright",
    "test",
]
nox.needs_version = ">=2022.1.7"


# used to reset cached coverage data once for the first test run only
reset_coverage = True


def depends(
    *deps: str,
    update: bool = True,
) -> Callable[[NoxSessionFunc[P, T]], NoxSessionFunc[P, T]]:
    """A session decorator that invokes :func:`.install` with the given parameters before running the session."""

    def decorator(f: NoxSessionFunc[P, T]) -> NoxSessionFunc[P, T]:
        @functools.wraps(f)
        def wrapper(session: nox.Session, *args: P.args, **kwargs: P.kwargs) -> T:
            nonlocal deps
            cmd = ["poetry", "install", "--sync"]
            if "main" not in deps:
                deps = ("main", *deps)

            for dep in deps:
                if dep in ("docs", "speed", "voice"):
                    arg = "--extras"
                else:
                    arg = "--only"
                cmd.extend([arg, dep])

            session.run_always(*cmd, external=True)
            return f(session, *args, **kwargs)

        return wrapper

    return decorator


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


@nox.session()
@depends("tools")
def slotscheck(session: nox.Session):
    """Run slotscheck."""
    session.run("python", "-m", "slotscheck", "--verbose", "-m", "disnake")


@nox.session(name="codemod")
@depends("tools")
def codemod(session: nox.Session):
    """Run libcst codemods."""
    if session.posargs and session.posargs[0] == "run-all" or not session.interactive:
        # run all of the transformers on disnake
        session.log("Running all transformers.")
        res: str = session.run("python", "-m", "libcst.tool", "list", silent=True)
        transformers = [line.split("-")[0].strip() for line in res.splitlines()]
        session.log("Transformers: " + ", ".join(transformers))

        for trans in transformers:
            session.run(
                "python", "-m", "libcst.tool", "codemod", trans, "disnake", "--hide-progress"
            )
        session.log("Finished running all transformers.")
    else:
        if session.posargs:
            if len(session.posargs) < 2:
                session.posargs.append("disnake")
            session.run(
                "python",
                "-m",
                "libcst.tool",
                "codemod",
                *session.posargs,
            )
        else:
            session.run("python", "-m", "libcst.tool", "list")


@nox.session()
@depends("tests", "docs", "speed", "voice", "typing")
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
@depends("tests", "typing")
def test(session: nox.Session, extras: List[str]):
    """Run tests."""
    # install(session, "dev", *extras)

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
@depends("tests")
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
