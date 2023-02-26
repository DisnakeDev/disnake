# SPDX-License-Identifier: MIT

from __future__ import annotations

import os
from itertools import chain
from typing import TYPE_CHECKING, Callable, List, TypeVar

import nox

if TYPE_CHECKING:
    from typing_extensions import Concatenate, ParamSpec

    P = ParamSpec("P")
    T = TypeVar("T")

    NoxSessionFunc = Callable[Concatenate[nox.Session, P], T]


# see https://pdm.fming.dev/latest/usage/advanced/#use-nox-as-the-runner
os.environ.update({"PDM_IGNORE_SAVED_PYTHON": "1"})

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


@nox.session
def docs(session: nox.Session):
    """Build and generate the documentation.

    If running locally, will build automatic reloading docs.
    If running in CI, will build a production version of the documentation.
    """
    session.run_always("pdm", "install", "--prod", "-G", "docs", external=True)
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


@nox.session
def lint(session: nox.Session):
    """Check all files for linting errors"""
    session.run_always("pdm", "install", "-G", "tools", external=True)

    session.run("pre-commit", "run", "--all-files", *session.posargs)


@nox.session(name="check-manifest")
def check_manifest(session: nox.Session):
    """Run check-manifest."""
    # --no-self is provided here because check-manifest builds disnake. There's no reason to build twice, so we don't.
    session.run_always("pdm", "install", "--no-self", "-dG", "tools", external=True)
    session.run("check-manifest", "-v")


@nox.session()
def slotscheck(session: nox.Session):
    """Run slotscheck."""
    session.run_always("pdm", "install", "-dG", "tools", external=True)
    session.run("python", "-m", "slotscheck", "--verbose", "-m", "disnake")


@nox.session(name="codemod")
def codemod(session: nox.Session):
    """Run libcst codemods."""
    session.run_always("pdm", "install", "-dG", "codemod", external=True)
    if session.posargs and session.posargs[0] == "run-all" or not session.interactive:
        # run all of the transformers on disnake
        session.log("Running all transformers.")
        res: str = session.run("python", "-m", "libcst.tool", "list", silent=True)  # type: ignore
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
def pyright(session: nox.Session):
    """Run pyright."""
    session.run_always("pdm", "install", "-d", "-Gspeed", "-Gdocs", "-Gvoice", external=True)
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
    # shell splitting is not done by nox
    extras = list(chain(*(["-G", extra] for extra in extras)))

    session.run_always("pdm", "install", "-dG", "test", "-dG", "typing", *extras, external=True)

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
def coverage(session: nox.Session):
    """Display coverage information from the tests."""
    session.run_always("pdm", "install", "-dG", "test", external=True)
    if "html" in session.posargs or "serve" in session.posargs:
        session.run("coverage", "html", "--show-contexts")
    if "serve" in session.posargs:
        session.run(
            "python", "-m", "http.server", "8012", "--directory", "htmlcov", "--bind", "127.0.0.1"
        )
    if "erase" in session.posargs:
        session.run("coverage", "erase")
