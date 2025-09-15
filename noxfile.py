#!/usr/bin/env -S pdm run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "nox==2025.5.1",
# ]
# ///

# SPDX-License-Identifier: MIT

from __future__ import annotations

import dataclasses
import os
import pathlib
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Union,
    overload,
)

import nox

nox.needs_version = ">=2025.5.1"


nox.options.error_on_external_run = True
nox.options.reuse_venv = "yes"

PYPROJECT = nox.project.load_toml()

SUPPORTED_PYTHONS = nox.project.python_versions(PYPROJECT)
# todo(onerandomusername): add 3.14 once CI supports 3.14.
EXPERIMENTAL_PYTHON_VERSIONS = ["3.14"]
CI = "CI" in os.environ

# used to reset cached coverage data once for the first test run only
reset_coverage = True


@dataclasses.dataclass
class ExecutionGroup:
    paths: Tuple[str, ...] = ()
    python: Optional[str] = None
    project: Optional[bool] = None
    extras: Tuple[str, ...] = ()
    groups: Tuple[str, ...] = ()
    dependencies: Tuple[str, ...] = ()
    experimental: bool = False
    sessions: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


EXECUTION_GROUPS: List[ExecutionGroup] = [
    ## pyright
    *(
        ExecutionGroup(
            python=python,
            paths=("disnake", "tests", "examples", "noxfile.py", "setup.py"),
            # orjson doesn't yet support python 3.14
            extras=("speed", "voice") if python not in EXPERIMENTAL_PYTHON_VERSIONS else ("voice",),
            groups=("test", "nox"),
            experimental=python in EXPERIMENTAL_PYTHON_VERSIONS,
            dependencies=("setuptools", "pytz", "requests"),  # needed for type checking
            sessions=("pyright",),
        )
        for python in [*SUPPORTED_PYTHONS, *EXPERIMENTAL_PYTHON_VERSIONS]
    ),
    # docs and pyright
    ExecutionGroup(
        python="3.8",
        paths=("docs",),
        extras=("docs",),
        experimental=True,
        sessions=("docs", "pyright"),
    ),
    # codemodding and pyright
    ExecutionGroup(
        python="3.8",
        paths=("scripts",),
        groups=("codemod",),
        experimental=True,
        sessions=("codemod", "pyright", "autotyping"),
    ),
    # the other sessions, they don't need pyright
    ExecutionGroup(
        python="3.8",
        paths=("disnake",),
        groups=("tools",),
        project=True,
        sessions=("lint", "slotscheck", "check-manifest"),
    ),
    ## testing
    *(
        ExecutionGroup(
            python=python,
            paths=("disnake", "tests"),
            groups=("test",),
            experimental=python in EXPERIMENTAL_PYTHON_VERSIONS,
            sessions=("test",),
        )
        for python in [*SUPPORTED_PYTHONS, *EXPERIMENTAL_PYTHON_VERSIONS]
    ),
    ExecutionGroup(
        python="3.11",
        paths=("disnake", "tests"),
        extras=("speed", "voice"),
        groups=("test",),
        sessions=("test",),
    ),
]


def get_groups_for_session(name: str) -> List[ExecutionGroup]:
    return [g for g in EXECUTION_GROUPS if name in g.sessions]


def get_version_for_session(name: str, *, exactly_one: bool = True) -> Union[str, List[str]]:
    possible_groups = get_groups_for_session(name)
    if exactly_one and len(possible_groups) != 1:
        raise TypeError(f"not the right number of groups for session {name}")
    return [g.python for g in possible_groups if g.python]


@overload
def install_deps(session: nox.Session, *, execution_group: ExecutionGroup) -> None: ...


@overload
def install_deps(
    session: nox.Session,
    *,
    extras: Iterable[str] = ...,
    groups: Iterable[str] = ...,
    dependencies: Iterable[str] = ...,
    project: bool = ...,
) -> None: ...


def install_deps(
    session: nox.Session,
    *,
    execution_group: Optional[ExecutionGroup] = None,
    extras: Iterable[str] = (),
    groups: Iterable[str] = (),
    dependencies: Iterable[str] = (),
    project: Optional[bool] = None,
) -> None:
    """Helper to install dependencies from a group."""
    if execution_group and any([extras, groups, dependencies, project is not None]):
        raise TypeError(
            "cannot provide execution_group and any of extras, groups, dependencies, or project"
        )

    if not execution_group and not any([extras, groups, dependencies, project is not None]):
        results = get_groups_for_session(session.name)
        if not results:
            # try cutting the `-`
            results = get_groups_for_session(session.name.split("-")[0])
        if len(results) != 1:
            raise TypeError(f"not a valid session name: {session.name}. results: {len(results)}")
        execution_group = results[0]

    if execution_group:
        extras = execution_group.extras
        groups = execution_group.groups
        dependencies = execution_group.dependencies
        project = execution_group.project if execution_group.project is not None else True

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


@nox.session(python=get_version_for_session("docs"), default=False)
def docs(session: nox.Session) -> None:
    """Build and generate the documentation.

    If running locally, will build automatic reloading docs.
    If running in CI, will build a production version of the documentation.
    """
    install_deps(session)
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
    """Check all paths for linting errors"""
    install_deps(session)
    session.run("pre-commit", "run", "--all-files", *session.posargs)


@nox.session(name="check-manifest")
def check_manifest(session: nox.Session) -> None:
    """Run check-manifest."""
    install_deps(session)
    session.run("check-manifest", "-v")


@nox.session(python=get_version_for_session("slotscheck"))
def slotscheck(session: nox.Session) -> None:
    """Run slotscheck."""
    install_deps(session)
    session.run("python", "-m", "slotscheck", "--verbose", "-m", "disnake")


@nox.session(python=get_version_for_session("autotyping"))
def autotyping(session: nox.Session) -> None:
    """Run autotyping.

    Because of the nature of changes that autotyping makes, and the goal design of examples,
    this runs on each folder in the repository with specific settings.
    """
    install_deps(session)
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


@nox.session(name="codemod", python=get_version_for_session("codemod"))
def codemod(session: nox.Session) -> None:
    """Run libcst codemods."""
    install_deps(session)

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
@nox.parametrize(
    ("python", "execution_group_dict"),
    [(group.python, group.to_dict()) for group in get_groups_for_session("pyright")],
    ids=[
        (group.python or "") + "-" + group.paths[0] for group in get_groups_for_session("pyright")
    ],
)
def pyright(session: nox.Session, execution_group_dict: Dict[str, Any]) -> None:
    execution_group = ExecutionGroup(**execution_group_dict)
    groups = execution_group.groups
    if "typing" not in groups:
        execution_group.groups = (*groups, "typing")
    install_deps(session, execution_group=execution_group)

    env = {
        "PYRIGHT_PYTHON_IGNORE_WARNINGS": "1",
    }
    try:
        session.run(
            "python",
            "-m",
            "pyright",
            *execution_group.paths,
            *session.posargs,
            env=env,
        )
    except KeyboardInterrupt:
        session.error("Quit pyright")
    except Exception:
        if not CI and execution_group.experimental:
            session.warn(
                "Pyright failed but the session was marked as experimental, exiting with 0"
            )
        else:
            raise


@nox.session()
@nox.parametrize(
    ("python", "execution_group_dict"),
    [(group.python, group.to_dict()) for group in get_groups_for_session("test")],
    ids=[
        (group.python or "")
        + "-"
        + group.paths[0]
        + (f"({'-'.join(group.extras)})" if group.extras else "")
        for group in get_groups_for_session("test")
    ],
)
def test(session: nox.Session, execution_group_dict: Dict[str, Any]) -> None:
    """Run tests."""
    execution_group = ExecutionGroup(**execution_group_dict)
    install_deps(session, execution_group=execution_group)

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

    This will:
    - lock all dependencies with pdm
    - create a .venv/ directory, overwriting the existing one,
    - install all dependencies needed for development.
    - install the pre-commit hook
    """
    session.run("pdm", "lock", "-dG:all", "-G:all", external=True)
    session.run("pdm", "venv", "create", "--force", external=True)
    session.run("pdm", "sync", "--clean-unselected", "-dG:all", "-G:all")
    session.run("pdm", "run", "pre-commit", "install")


if __name__ == "__main__":
    nox.main()
