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
from typing import Any, Dict, List, Sequence, Tuple

import nox

nox.needs_version = ">=2025.5.1"


nox.options.error_on_external_run = True
nox.options.reuse_venv = "yes"
nox.options.sessions = [
    "lint",
    "check-manifest",
    "slotscheck",
    "pyright",
    "test",
]

PYPROJECT = nox.project.load_toml()
CI = "CI" in os.environ

# used to reset cached coverage data once for the first test run only
reset_coverage = True


def install_deps(
    session: nox.Session,
    *,
    extras: Sequence[str] = (),
    groups: Sequence[str] = (),
    dependencies: Sequence[str] = (),
    project: bool = True,
) -> None:
    """Helper to install dependencies from a group."""
    if not project and extras:
        raise TypeError("Cannot install extras without also installing the project")

    command: List[str]

    # If not using pdm, install with pip
    if os.getenv("NO_PDM_INSTALL") is not None:
        command = []
        if project:
            command.append("-e")
            command.append(".")
            if extras:
                # project[extra1,extra2]
                command[-1] += "[" + ",".join(extras) + "]"
        if groups:
            command.extend(nox.project.dependency_groups(PYPROJECT, *groups))
        session.install(*command)

        # install separately in case it conflicts with a just-installed dependency (for overriding a locked dep)
        if dependencies:
            session.install(*dependencies)

        return

    # install with pdm
    command = [
        "pdm",
        "sync",
        "--fail-fast",
        "--clean-unselected",
    ]

    # see https://pdm-project.org/latest/usage/advanced/#use-nox-as-the-runner
    env: Dict[str, Any] = {
        "PDM_IGNORE_SAVED_PYTHON": "1",
    }

    command.extend([f"-G={g}" for g in (*extras, *groups)])

    if not groups:
        # if no dev groups requested, make sure we don't install any
        command.append("--prod")

    if not project:
        command.append("--no-self")

    session.run_install(
        *command,
        env=env,
        external=True,
    )

    if dependencies:
        if session.venv_backend == "none" and CI:
            # we are not in a venv but we're on CI so we probably intended to do this
            session.run_install("pip", "install", *dependencies, env=env)
        else:
            session.install(*dependencies, env=env)


@nox.session(python="3.8")
def docs(session: nox.Session) -> None:
    """Build and generate the documentation.

    If running locally, will build automatic reloading docs.
    If running in CI, will build a production version of the documentation.
    """
    install_deps(session, extras=["docs"])
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
    install_deps(session, project=False, groups=["tools"])

    session.run("pre-commit", "run", "--all-files", *session.posargs)


@nox.session(name="check-manifest")
def check_manifest(session: nox.Session) -> None:
    """Run check-manifest."""
    install_deps(session, project=False, groups=["tools"])
    session.run("check-manifest", "-v")


@nox.session
def slotscheck(session: nox.Session) -> None:
    """Run slotscheck."""
    install_deps(session, project=True, groups=["tools"])
    session.run("python", "-m", "slotscheck", "--verbose", "-m", "disnake")


@nox.session
def autotyping(session: nox.Session) -> None:
    """Run autotyping.

    Because of the nature of changes that autotyping makes, and the goal design of examples,
    this runs on each folder in the repository with specific settings.
    """
    install_deps(session, project=True, groups=["codemod"])

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
    install_deps(session, project=True, groups=["codemod"])

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


@nox.session
def pyright(session: nox.Session) -> None:
    """Run pyright."""
    install_deps(
        session,
        project=True,
        extras=[
            "speed",
            "voice",
            "docs",  # docs/
        ],
        groups=[
            "test",  # tests/
            "nox",  # noxfile.py
            "codemod",  # scripts/
            "typing",  # pyright
        ],
        dependencies=["setuptools"],
    )
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
    install_deps(session, project=True, extras=extras, groups=["test"])

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


@nox.session
def coverage(session: nox.Session) -> None:
    """Display coverage information from the tests."""
    install_deps(session, project=False, groups=["test"])

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


if __name__ == "__main__":
    nox.main()
