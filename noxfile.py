# SPDX-License-Identifier: MIT


from __future__ import annotations

import pathlib
from typing import Dict, List, Optional, Sequence, Tuple

import nox

PYPROJECT = nox.project.load_toml()

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
nox.needs_version = ">=2025.5.1"


# used to reset cached coverage data once for the first test run only
reset_coverage = True

EMPTY_SEQUENCE: Sequence[str] = set()  # type: ignore


# Helper to install dependencies from a group, using uv if venv_backend is uv
def install_deps(
    session: nox.Session,
    *,
    extras: Sequence[str] = EMPTY_SEQUENCE,
    groups: Sequence[str] = EMPTY_SEQUENCE,
    project: bool = True,
    fork_strategy: Optional[str] = None,
    resolution: Optional[str] = None,
) -> None:
    if not project and extras:  # cannot install extras without also installing the project
        raise TypeError("Cannot install extras without also installing the project")

    command: List[str] = []

    # If not using uv, install with pip
    if getattr(session, "venv_backend", None) != "uv":
        if project:
            command.append("-e")
            command.append(".")
            if extras:
                command[-1] += "[" + ",".join(extras) + "]"
        if groups:
            command.extend(nox.project.dependency_groups(PYPROJECT, *groups))
        session.install(*command)
        return None

    # install with UV
    command = [
        "uv",
        "sync",
        f"--python={session.virtualenv.location}",
        "--no-default-groups",
    ]
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
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )


@nox.session
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
    install_deps(session, groups=["tools"])

    session.run("pre-commit", "run", "--all-files", *session.posargs)


@nox.session(name="check-manifest")
def check_manifest(session: nox.Session) -> None:
    """Run check-manifest."""
    install_deps(session, groups=["tools"])
    session.run("check-manifest", "-v")


@nox.session()
def slotscheck(session: nox.Session) -> None:
    """Run slotscheck."""
    install_deps(session, groups=["tools"])
    session.run("python", "-m", "slotscheck", "--verbose", "-m", "disnake")


@nox.session
def autotyping(session: nox.Session) -> None:
    """Run autotyping.

    Because of the nature of changes that autotyping makes, and the goal design of examples,
    this runs on each folder in the repository with specific settings.
    """
    install_deps(session, project=False, groups=["codemod"])

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


@nox.session(name="codemod")
def codemod(session: nox.Session) -> None:
    """Run libcst codemods."""
    install_deps(session, groups=["codemod"])

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
            "test",
            "nox",
            "changelog",
            "docs",
            "codemod",
            "typing",
            "tools",
        ],
    )
    env = {
        "PYRIGHT_PYTHON_IGNORE_WARNINGS": "1",
    }
    try:
        session.run("python", "-m", "pyright", *session.posargs, env=env)
    except KeyboardInterrupt:
        pass


@nox.session(python=["3.8", "3.9", "3.10", "3.11", "3.12", "3.13"])
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
