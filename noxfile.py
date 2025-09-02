#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "nox==2025.5.01",
# ]
# ///
# SPDX-License-Identifier: MIT


from __future__ import annotations

import os
import pathlib
import sys
from typing import Any, Dict, List, Optional, Sequence, Tuple

import nox

nox.needs_version = ">=2025.5.1"

PYPROJECT = nox.project.load_toml()


def use_min_python_of(python: str, *, preferred: Optional[str] = None) -> str | None:
    """Use the minimum necessary python for this run, but if the environment is a specific venv, then use that one."""
    major, minor = python.split(".")
    if sys.version_info < (int(major), int(minor)):
        # If the current Python version is less than the required version, use the required version
        return preferred or python
    return None


nox.options.error_on_external_run = True
nox.options.reuse_venv = "yes"
nox.options.default_venv_backend = "uv|virtualenv"
nox.options.sessions = [
    "lint",
    "check-manifest",
    "slotscheck",
    "pyright",
    "test",
]


# used to reset cached coverage data once for the first test run only
reset_coverage = True

EMPTY_SEQUENCE: Sequence[str] = ()


def install_deps(
    session: nox.Session,
    *,
    extras: Sequence[str] = EMPTY_SEQUENCE,
    groups: Sequence[str] = EMPTY_SEQUENCE,
    dependencies: Sequence[str] = EMPTY_SEQUENCE,  # a parameter itself for pip
    project: bool = True,
) -> None:
    """Helper to install dependencies from a group, using uv if venv_backend is uv."""
    if not project and extras:
        raise TypeError("Cannot install extras without also installing the project")

    command: List[str] = []

    force_use_uv = os.getenv("CI") is not None and session.venv_backend == "none"

    # If not using uv, install with pip
    if not force_use_uv and session.venv_backend != "uv":
        if project:
            command.append("-e")
            command.append(".")
            if extras:
                command[-1] += "[" + ",".join(extras) + "]"
        if groups:
            command.extend(nox.project.dependency_groups(PYPROJECT, *groups))
        session.install(*command)
        # install separately in case it conflicts with a just-installed dependency (for overriding a locked dep)
        if dependencies:
            session.install(*dependencies)
        return None

    # install with UV
    command = [
        "uv",
        "sync",
        "--no-default-groups",
    ]
    env: Dict[str, Any] = {}

    if not force_use_uv:
        command.append(f"--python={session.virtualenv.location}")
        env["UV_PROJECT_ENVIRONMENT"] = str(session.virtualenv.location)

    if extras:
        for e in extras:
            command.append(f"--extra={e}")
    if groups:
        for g in groups:
            command.append(f"--group={g}")
    if not project:
        command.append("--no-install-project")

    session.run_install(
        *command,
        env=env,
    )

    if dependencies:
        if force_use_uv:
            session.run_install("uv", "pip", "install", *dependencies)
        else:
            # this will use uv as it is the runner
            session.install(*dependencies)


@nox.session(reuse_venv=True, python="3.8")
def docs(session: nox.Session) -> None:
    """Build and generate the documentation.

    If running locally, will build automatic reloading docs.
    If running in CI, will build a production version of the documentation.
    """
    install_deps(session, groups=["docs"])
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


@nox.session()
def slotscheck(session: nox.Session) -> None:
    """Run slotscheck."""
    install_deps(session, project=False, groups=["tools"])
    session.run("python", "-m", "slotscheck", "--verbose", "-m", "disnake")


@nox.session(requires=["check-manifest"])
def build(session: nox.Session) -> None:
    """Build a dist."""
    import pathlib

    dist_path = pathlib.Path("dist")
    if dist_path.exists():
        import shutil

        shutil.rmtree(dist_path)
    install_deps(session, project=False, dependencies=["build"])
    session.run("python", "-m", "build", "--outdir", "dist")


@nox.session(python=use_min_python_of("3.11", preferred="3.13"))
def autotyping(session: nox.Session) -> None:
    """Run autotyping.

    Because of the nature of changes that autotyping makes, and the goal design of examples,
    this runs on each folder in the repository with specific settings.
    """
    install_deps(
        session,
        project=False,
        groups=["codemod"],
        dependencies=["libcst==1.8.2"],
    )

    base_command = ["python", "-m", "libcst.tool", "codemod", "autotyping.AutotypeCommand"]
    if not session.interactive:
        base_command += ["--hide-progress"]

    dir_options: Dict[Tuple[str, ...], Tuple[str, ...]] = {
        (
            "disnake",
            "scripts",
            "tests",
            "test_bot",
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


@nox.session(name="codemod", python=use_min_python_of("3.11", preferred="3.13"))
def codemod(session: nox.Session) -> None:
    """Run libcst codemods."""
    install_deps(
        session,
        groups=["codemod"],
        dependencies=["libcst==1.8.2"],
    )

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
    install_deps(
        session,
        project=True,
        extras=["speed", "voice"],
        groups=[
            "test",  # tests/
            "nox",  # noxfile.py
            "docs",  # docs/
            "tools",  # test_bot/ uses python-dotenv
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
    install_deps(session, project=True, extras=extras, groups=["test", "typing"])

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
    install_deps(session, project=True, groups=["test"])
    if "html" in session.posargs or "serve" in session.posargs:
        session.run("coverage", "html", "--show-contexts")
    if "serve" in session.posargs:
        session.run(
            "python", "-m", "http.server", "8012", "--directory", "htmlcov", "--bind", "127.0.0.1"
        )
    if "erase" in session.posargs:
        session.run("coverage", "erase")


@nox.session(default=False, python=False)
def dev(session: nox.Session) -> None:
    """Set up a development environment using uv.

    This will create a .venv/ directory if it does not exist, and install all dependencies
    needed for development.

    If a .python-version file does not exist, it will be created with the earliest supported
    Python version from pyproject.toml.
    """
    import pathlib

    if not pathlib.Path(".python-version").exists():
        session.log(".python-version file does not exist, creating one...")
        python_version = nox.project.python_versions(PYPROJECT)[0]
        session.run(
            "uv",
            "python",
            "pin",
            python_version,  # use the earliest supported python version if not already pinned
            external=True,
        )
        session.log(f"Pinned local python version to {python_version}.")
    else:
        session.log(".python-version file already exists, not modifying it.")

    env = {
        "UV_PROJECT_ENVIRONMENT": str(pathlib.Path(".venv").absolute()),
        "VIRTUAL_ENV": str(pathlib.Path(".venv").absolute()),
    }
    session.log("Creating a new virtual environment with uv...")
    session.run("uv", "venv", ".venv", "--allow-existing", external=True, env=env)

    session.log("Creating a `uv.lock` file/updating it with the current dependencies...")
    session.run("uv", "lock", external=True, env=env)

    session.log("Installing all dependencies...")
    session.run("uv", "sync", "--all-extras", "--all-groups", external=True, env=env)

    git_pre_commit_path = pathlib.Path(".git/hooks/pre-commit")
    if not git_pre_commit_path.exists() or not git_pre_commit_path.read_text().find(
        "# File generated by pre-commit: https://pre-commit.com"
    ):
        session.log("Creating pre-commit hook...")
        session.run("uv", "run", "pre-commit", "install", "--install-hooks", external=True, env=env)
    else:
        session.log("Pre-commit hook already exists, not modifying it.")

    session.log("Installing pre-commit hook environments...")
    session.run("uv", "run", "pre-commit", "install-hooks", external=True, env=env)

    session.log("Creating all nox environments...")

    session.run(
        "nox",
        "-N",
        "--install-only",
        env=env,
        external=False,  # force use ourselves
        silent=True,
    )


if __name__ == "__main__":
    nox.main()
