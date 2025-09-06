#!/usr/bin/env -S pdm run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "nox==2025.5.1",
# ]
# ///

# SPDX-License-Identifier: MIT

from __future__ import annotations

import os
import pathlib
from itertools import chain
from typing import TYPE_CHECKING, Callable, Dict, List, Tuple, TypeVar

import nox

if TYPE_CHECKING:
    from typing_extensions import Concatenate, ParamSpec

    P = ParamSpec("P")
    T = TypeVar("T")

    NoxSessionFunc = Callable[Concatenate[nox.Session, P], T]

nox.needs_version = ">=2025.5.1"

PYPROJECT = nox.project.load_toml()

# see https://pdm-project.org/latest/usage/advanced/#use-nox-as-the-runner
os.environ.update(
    {
        "PDM_IGNORE_SAVED_PYTHON": "1",
    },
)

nox.options.error_on_external_run = True
nox.options.reuse_existing_virtualenvs = True
nox.options.sessions = [
    "lint",
    "check-manifest",
    "slotscheck",
    "pyright",
    "test",
]

PYPROJECT = nox.project.load_toml()

# used to reset cached coverage data once for the first test run only
reset_coverage = True


@nox.session(python="3.8")
def docs(session: nox.Session) -> None:
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
def lint(session: nox.Session) -> None:
    """Check all files for linting errors"""
    session.run_always("pdm", "install", "-G", "tools", external=True)

    session.run("pre-commit", "run", "--all-files", *session.posargs)


@nox.session(name="check-manifest")
def check_manifest(session: nox.Session) -> None:
    """Run check-manifest."""
    # --no-self is provided here because check-manifest builds disnake. There's no reason to build twice, so we don't.
    session.run_always("pdm", "install", "--no-self", "-dG", "tools", external=True)
    session.run("check-manifest", "-v")


@nox.session()
def slotscheck(session: nox.Session) -> None:
    """Run slotscheck."""
    session.run_always("pdm", "install", "-dG", "tools", external=True)
    session.run("python", "-m", "slotscheck", "--verbose", "-m", "disnake")


@nox.session
def autotyping(session: nox.Session) -> None:
    """Run autotyping.

    Because of the nature of changes that autotyping makes, and the goal design of examples,
    this runs on each folder in the repository with specific settings.
    """
    session.run_always("pdm", "install", "-dG", "codemod", external=True)

    base_command = ["python", "-m", "libcst.tool", "codemod", "autotyping.AutotypeCommand"]
    if not session.interactive:
        base_command += ["--hide-progress"]

    dir_options: Dict[Tuple[str, ...], Tuple[str, ...]] = {
        (
            "disnake",
            "scripts",
            "tests",
            "noxfile.py",
        ): ("--aggressive",),
        ("examples",): (
            "--scalar-return",
            "--bool-param",
            "--bool-param",
            "--int-param",
            "--float-param",
            "--str-param",
            "--bytes-param",
        ),
    }

    if session.posargs:
        # short circuit with the provided arguments
        # if there's just one file argument, give it the defaults that we normally use
        posargs = session.posargs.copy()
        if len(posargs) == 1 and not (path := posargs[0]).startswith("--"):
            path = pathlib.Path(path).absolute()
            try:
                path = path.relative_to(pathlib.Path.cwd())
            except ValueError:
                pass
            else:
                module = path.parts[0]
                for modules, options in dir_options.items():
                    if module in modules:
                        posargs += options
                        break

        session.run(
            *base_command,
            *posargs,
        )
        return

    # run the custom fixers
    for module, options in dir_options.items():
        session.run(
            *base_command,
            *module,
            *options,
        )


@nox.session(name="codemod", python="3.8")
def codemod(session: nox.Session) -> None:
    """Run libcst codemods."""
    session.run_always("pdm", "install", "-dG", "codemod", external=True)

    base_command = ["python", "-m", "libcst.tool"]
    base_command_codemod = [*base_command, "codemod"]
    if not session.interactive:
        base_command_codemod += ["--hide-progress"]

    if (session.posargs and session.posargs[0] == "run-all") or not session.interactive:
        # run all of the transformers on disnake
        session.log("Running all transformers.")

        session.run(*base_command_codemod, "combined.CombinedCodemod", "disnake")
    elif session.posargs:
        if len(session.posargs) < 2:
            session.posargs.append("disnake")

        session.run(*base_command_codemod, *session.posargs)
    else:
        session.run(*base_command, "list")
        return  # don't run autotyping in this case

    session.notify("autotyping", posargs=[])


@nox.session()
def pyright(session: nox.Session) -> None:
    """Run pyright."""
    session.run_always("pdm", "install", "-d", "-Gspeed", "-Gdocs", "-Gvoice", external=True)
    env = {
        "PYRIGHT_PYTHON_IGNORE_WARNINGS": "1",
    }
    try:
        session.run("python", "-m", "pyright", *session.posargs, env=env)
    except KeyboardInterrupt:
        pass


@nox.session(python=nox.project.python_versions(PYPROJECT))
@nox.parametrize(
    "extras",
    [
        [],
        # NOTE: disabled while there are no tests that would require these dependencies
        # ["speed"],
        # ["voice"],
    ],
)
def test(session: nox.Session, extras: List[str]) -> None:
    """Run tests."""
    # shell splitting is not done by nox
    extras = list(chain(*(["-G", extra] for extra in extras)))

    session.run_always("pdm", "install", "-dG", "test", "-dG", "typing", *extras, external=True)

    pytest_args = ["--cov", "--cov-context=test"]
    global reset_coverage  # noqa: PLW0603
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
def coverage(session: nox.Session) -> None:
    """Display coverage information from the tests."""
    session.run_always("pdm", "install", "-dG", "test", external=True)
    posargs = session.posargs
    # special-case serve
    if "serve" in posargs:
        if len(posargs) != 1:
            session.error("serve cannot be used with any other arguments.")
        session.run("coverage", "html", "--show-contexts")
        session.run(
            "python", "-m", "http.server", "8012", "--directory", "htmlcov", "--bind", "127.0.0.1"
        )
        return

    session.run("coverage", *posargs)


@nox.session(default=False, python=False)
def dev(session: nox.Session) -> None:
    """Set up a development environment using uv.

    This will create a .venv/ directory if it does not exist, and install all dependencies
    needed for development.

    If a .python-version file does not exist, it will be created with the earliest supported
    Python version from pyproject.toml.
    """
    import pathlib

    python_version = nox.project.python_versions(PYPROJECT)[0]
    if not pathlib.Path(".venv").exists():
        # this will only run if the file is ran with nox or as a script directly
        session.run("pdm", "venv", "create", python_version)

    if not pathlib.Path("pdm.lock").exists():
        session.debug("Creating a `pdm.lock` file...")
        session.run("pdm", "lock", "-G:all", "-dG:all", "--python=>=3.8")

    session.debug("Installing all dependencies...")
    session.run("pdm", "sync", "-G:all", "-dG:all")

    git_pre_commit_path = pathlib.Path(".git/hooks/pre-commit")
    if not git_pre_commit_path.exists() or not git_pre_commit_path.read_text().find(
        "# File generated by pre-commit: https://pre-commit.com"
    ):
        session.debug("Creating pre-commit hook...")
        session.run("pdm", "run", "pre-commit", "install", "--install-hooks")
    else:
        session.warn("Pre-commit hook already exists, not modifying it.")

    session.debug("Installing pre-commit hook environments...")
    session.run("pdm", "run", "pre-commit", "install-hooks")

    session.debug("Creating all nox environments...")
    session.run(
        "nox",
        "--install-only",
        *session.posargs,
    )


if __name__ == "__main__":
    nox.main()
