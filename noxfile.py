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

# used to reset cached coverage data once for the first test run only
reset_coverage = True


def install_deps(
    session: nox.Session,
    *,
    extras: Sequence[str] = (),
    groups: Sequence[str] = (),
    project: bool = True,
) -> None:
    """Helper to install dependencies from a group."""
    if not project and extras:
        raise TypeError("Cannot install extras without also installing the project")

    command: List[str] = [
        "pdm",
        "sync",
        "--fail-fast",
        "--clean-unselected",
    ]

    # see https://pdm-project.org/latest/usage/advanced/#use-nox-as-the-runner
    env: Dict[str, Any] = {
        "PDM_IGNORE_SAVED_PYTHON": "1",
        "PDM_FROZEN_LOCKFILE": "1",
        "VIRTUAL_ENV": session.virtualenv.location,
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
        extras=["speed", "voice"],
        groups=[
            "test",  # tests/
            "nox",  # noxfile.py
            "docs",  # docs/
            "codemod",  # scripts/
            "typing",  # pyright
        ],
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


@nox.session(default=False, python=False)
def dev(session: nox.Session) -> None:
    """Set up a development environment using pdm.

    This will create a .venv/ directory if it does not exist, and install all dependencies
    needed for development.

    Arguments:
    --python <version>  Specify the Python version to use for the virtual environment.
                          If not provided, uses the current Python version if it meets the
                          minimum requirement of Python 3.8, otherwise uses Python 3.8.
    --resolution <mode> Set the dependency resolution mode for uv. Can be 'highest', 'lowest', or 'lowest-direct'.
    --frozen            Skip updating the uv.lock file. Useful for CI environments to ensure
                          dependencies are not changed.
    --no-venv           Skip creating a virtual environment. Useful if you want to use
                          an existing virtual environment.
    --no-nox            Skip creating nox environments. Useful if you only want to set up the
                          main virtual environment.
    --no-upgrade        Skip upgrading dependencies in the uv.lock file.
    --no-sync           Skip installing dependencies. Useful if you only want to set up the
                          virtual environment and not install packages.
    """
    # lazy import because this session is only run once per dev environment
    import pathlib

    env = {
        "VIRTUAL_ENV": str(pathlib.Path(".venv").absolute()),
    }

    if "-h" in session.posargs or "--help" in session.posargs:
        session.log(dev.__doc__)
        return

    python_version: str = ""
    if "--python" in session.posargs:
        python_version_index = session.posargs.index("--python") + 1
        if python_version_index >= len(session.posargs):
            session.error("No Python version specified after --python")
        python_version = session.posargs[python_version_index]
        session.posargs.pop(python_version_index)  # remove the version
        session.posargs.pop(python_version_index - 1)  # remove the --python

    # check that the python version matches the existing venv if no-venv is provided
    if "--no-venv" in session.posargs and pathlib.Path(".venv").exists() and python_version:
        version = session.run(
            "pdm",
            "info",
            "--python",
            external=True,
            env=env,
            silent=True,
        )
        if version and version.strip().split(".", 2)[:2] != python_version.split(".", 2)[:2]:
            session.error(
                f"Python version mismatch: venv has {version.strip()}, but --python specifies {python_version}"
            )

    if python_version:
        env["PDM_USE_PYTHON_VERSION"] = python_version

    if "--no-venv" in session.posargs:
        session.debug("Skipping creating a venv")
        session.posargs.remove("--no-venv")
    else:
        session.debug("Creating a new virtual environment with pdm...")
        session.run("pdm", "create", "venv", ".venv", "--allow-existing", external=True, env=env)

    lock_args = []
    should_lock = True
    if "--resolution" in session.posargs:
        env["UV_RESOLUTION"] = session.posargs[session.posargs.index("--resolution") + 1]
        session.posargs.pop(session.posargs.index("--resolution") + 1)
        session.posargs.remove("--resolution")
    elif "UV_RESOLUTION" not in os.environ:
        env["UV_RESOLUTION"] = "highest"
    if (
        os.environ.get("PDM_FROZEN_LOCKFILE") in ("1", "true", "True")
        or "--frozen" in session.posargs
    ):
        if "--frozen" in session.posargs:
            should_lock = False
            session.posargs.remove("--frozen")
        should_lock = False
    if "--no-upgrade" in session.posargs:
        lock_args.remove("--upgrade")
        session.posargs.append("--update-reuse")
    if should_lock:
        session.debug("Creating a `pdm.lock` file/updating it with the current dependencies...")
        session.run("pdm", "lock", *lock_args, external=True, env=env)
    else:
        session.debug("Skipping locking dependencies.")

    if "UV_NO_SYNC" not in os.environ and "--no-sync" not in session.posargs:
        session.debug("Installing all dependencies...")
        session.run("pdm", "sync", "-G:all", "-dG:all", external=True, env=env)
    else:
        session.debug("Skipping installing dependencies.")

    git_pre_commit_path = pathlib.Path(".git/hooks/pre-commit")
    if not git_pre_commit_path.exists() or not git_pre_commit_path.read_text().find(
        "# File generated by pre-commit: https://pre-commit.com"
    ):
        session.debug("Creating pre-commit hook...")
        session.run(
            "pdm",
            "run",
            "pre-commit",
            "install",
            "--install-hooks",
            external=True,
            env=env,
        )
    else:
        session.warn("Pre-commit hook already exists, not modifying it.")

    if "--no-nox" in session.posargs:
        session.debug("Skipping creating nox environments.")
        return

    session.debug("Creating all nox environments...")

    # this creates every session's venv
    # which we do to proactively download all dependencies
    session.run(
        "nox",
        "-N",
        "--install-only",
        *session.posargs,
        env=env,
        external=False,  # force use ourselves
        # silent=not session.posargs,  # only be quiet if there's no arguments
    )


if __name__ == "__main__":
    nox.main()
