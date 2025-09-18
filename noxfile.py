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
    TYPE_CHECKING,
    Any,
    Dict,
    Final,
    List,
    Optional,
    Set,
    Tuple,
)

import nox

nox.needs_version = ">=2025.5.1"


nox.options.error_on_external_run = True
nox.options.reuse_venv = "yes"
nox.options.default_venv_backend = "uv|virtualenv"

PYPROJECT = nox.project.load_toml()

SUPPORTED_PYTHONS: Final[List[str]] = nox.project.python_versions(PYPROJECT)
# TODO(onerandomusername): add 3.14 once CI supports 3.14.
EXPERIMENTAL_PYTHON_VERSIONS: Final[List[str]] = []
ALL_PYTHONS: Final[List[str]] = [*SUPPORTED_PYTHONS, *EXPERIMENTAL_PYTHON_VERSIONS]
MIN_PYTHON: Final[str] = SUPPORTED_PYTHONS[0]
CI: Final[bool] = "CI" in os.environ

# used to reset cached coverage data once for the first test run only
reset_coverage = True
# used to only show the pyright warning once
pyright_warning_shown = False

if TYPE_CHECKING:
    ExecutionGroupType = object
else:
    ExecutionGroupType = Dict[str, Any]


@dataclasses.dataclass(frozen=True)
class ExecutionGroup(ExecutionGroupType):
    sessions: Tuple[str, ...] = ()
    python: str = MIN_PYTHON
    project: bool = True
    extras: Tuple[str, ...] = ()
    groups: Tuple[str, ...] = ()
    dependencies: Tuple[str, ...] = ()
    experimental: bool = False
    pyright_paths: Tuple[str, ...] = ()
    tags: Dict[str, Tuple[str, ...]] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.experimental:
            object.__setattr__(
                self,
                "experimental",
                self.python in EXPERIMENTAL_PYTHON_VERSIONS,
            )
        if self.pyright_paths and "pyright" not in self.sessions:
            raise TypeError("pyright_paths can only be set if pyright is in sessions")
        for key in self.__dataclass_fields__.keys():
            self[key] = getattr(self, key)  # type: ignore

    @property
    def pyright_session_id(self) -> str:
        return (self.python or "") + "-" + self.pyright_paths[0]

    @property
    def test_session_id(self) -> str:
        return (self.python or "") + (f"({'-'.join(self.extras)})" if self.extras else "")


EXECUTION_GROUPS: List[ExecutionGroup] = [
    ## pyright
    *(
        ExecutionGroup(
            sessions=("pyright",),
            python=python,
            pyright_paths=("disnake", "tests", "examples", "noxfile.py", "setup.py"),
            project=True,
            # FIXME: orjson doesn't yet support python 3.14, remove once we migrate to uv and have version-specific locks
            extras=("speed", "voice") if python not in EXPERIMENTAL_PYTHON_VERSIONS else ("voice",),
            groups=("test", "nox"),
            dependencies=("setuptools", "pytz", "requests"),  # needed for type checking
            tags={
                "pyright": tuple(
                    x
                    for x in (
                        "ci",
                        "typing",
                        "quick" if python in (MIN_PYTHON, SUPPORTED_PYTHONS[-1]) else None,
                    )
                    if x
                ),
            },
        )
        for python in ALL_PYTHONS
    ),
    # docs and pyright
    ExecutionGroup(
        sessions=("docs", "pyright"),
        pyright_paths=("docs",),
        extras=("docs",),
        tags={"pyright": ("docs", "ci")},
    ),
    # codemodding and pyright
    ExecutionGroup(
        sessions=("codemod", "autotyping", "pyright"),
        pyright_paths=("scripts",),
        groups=("codemod",),
        tags={"pyright": ("scripts", "ci")},
    ),
    # the other sessions, they don't need pyright, but they need to run
    ExecutionGroup(
        sessions=("lint", "slotscheck", "check-manifest"),
        groups=("tools",),
    ),
    ## testing
    *(
        ExecutionGroup(
            sessions=("test",),
            python=python,
            groups=("test",),
            tags={
                "test": tuple(
                    x
                    for x in (
                        "ci",
                        "quick" if python in (MIN_PYTHON, SUPPORTED_PYTHONS[-1]) else None,
                    )
                    if x
                ),
            },
        )
        for python in ALL_PYTHONS
    ),
    # coverage
    ExecutionGroup(
        sessions=("coverage",),
        project=False,
        groups=("test",),
    ),
]


def get_groups_for_session(name: str) -> List[ExecutionGroup]:
    return [g for g in EXECUTION_GROUPS if name in g.sessions]


def check_paths(session: nox.Session, paths: List[str], group: ExecutionGroup) -> List[str]:
    """Check that the provided paths are valid for the given group."""
    paths = []
    for arg in session.posargs:
        if arg.startswith("-"):
            paths.append(arg)
            continue
        if any(
            arg == pyright_path
            or arg.startswith((f"{pyright_path}{os.path.sep}", f"{pyright_path}/"))
            for pyright_path in group.pyright_paths
        ):
            paths.append(arg)
            continue

    return paths


def get_version_for_session(name: str) -> str:
    versions = {g.python for g in get_groups_for_session(name) if g.python}
    if len(versions) != 1:
        raise TypeError(f"not the right number of groups for session {name}")
    return versions.pop()


def install_deps(session: nox.Session, *, execution_group: Optional[ExecutionGroup] = None) -> None:
    """Helper to install dependencies from a group."""
    if not execution_group:
        results = get_groups_for_session(session.name)
        if not results:
            # try cutting the `-`
            results = get_groups_for_session(session.name.split("-")[0])
        if len(results) != 1:
            raise TypeError(f"not a valid session name: {session.name}. results: {len(results)}")
        execution_group = results[0]

    if not execution_group.project and execution_group.extras:
        raise TypeError("Cannot install extras without also installing the project")

    command: List[str]

    # If not using pdm, install with pip
    if os.getenv("NO_PDM_INSTALL") is not None:
        command = []
        if execution_group.project:
            command.append("-e")
            command.append(".")
            if execution_group.extras:
                # project[extra1,extra2]
                command[-1] += "[" + ",".join(execution_group.extras) + "]"
        if execution_group.groups:
            command.extend(nox.project.dependency_groups(PYPROJECT, *execution_group.groups))
        session.install(*command)

        # install separately in case it conflicts with a just-installed dependency (for overriding a locked dep)
        if execution_group.dependencies:
            session.install(*execution_group.dependencies)

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

    command.extend([f"-G={g}" for g in (*execution_group.extras, *execution_group.groups)])

    if not execution_group.groups:
        # if no dev groups requested, make sure we don't install any
        command.append("--prod")

    if not execution_group.project:
        command.append("--no-self")

    session.run_install(
        *command,
        env=env,
        external=True,
    )

    if execution_group.dependencies:
        if session.venv_backend == "none" and CI:
            # we are not in a venv but we're on CI so we probably intended to do this
            session.run_install("pip", "install", *execution_group.dependencies, env=env)
        else:
            session.install(*execution_group.dependencies, env=env)


@nox.session(python=get_version_for_session("docs"), tags=("ci", "docs"), default=False)
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


@nox.session(tags=("ci", "quick", "fix"))
def lint(session: nox.Session) -> None:
    """Check all paths for linting errors"""
    install_deps(session)
    session.run("pre-commit", "run", "--all-files", *session.posargs)


@nox.session(name="check-manifest", tags=("ci", "build"))
def check_manifest(session: nox.Session) -> None:
    """Run check-manifest."""
    install_deps(session)
    session.run("check-manifest", "-v")


@nox.session(python=get_version_for_session("slotscheck"), tags=("ci",))
def slotscheck(session: nox.Session) -> None:
    """Run slotscheck."""
    install_deps(session)
    session.run("python", "-m", "slotscheck", "--verbose", "-m", "disnake")


@nox.session(
    name="codemod",
    python=get_version_for_session("codemod"),
    tags=("ci", "typehints", "fix", "scripts"),
)
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


@nox.session(
    python=get_version_for_session("autotyping"),
    tags=("ci", "codemod", "typehints", "fix"),
)
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


@nox.session()
@nox.parametrize(
    ("python", "execution_group"),
    [(group.python, group) for group in get_groups_for_session("pyright")],
    ids=[group.pyright_session_id for group in get_groups_for_session("pyright")],
    tags=[group.tags.get("pyright", []) for group in get_groups_for_session("pyright")],
)
def pyright(session: nox.Session, execution_group: ExecutionGroup, **kwargs: Any) -> None:
    if paths := session.posargs:
        paths = check_paths(session, session.posargs, execution_group)
        if not paths:
            session.skip(
                "Provided paths do not match this session's pyright paths.",
            )
    groups = execution_group.groups
    if "typing" not in groups:
        # typing is not included because these groups can be reused for other tasks that don't need pyright
        execution_group = dataclasses.replace(execution_group, groups=(*groups, "typing"))
    install_deps(session, execution_group=execution_group)

    env = {
        "PYRIGHT_PYTHON_IGNORE_WARNINGS": "1",
    }
    try:
        session.run(
            "python",
            "-m",
            "pyright",
            *(paths or execution_group.pyright_paths),
            env=env,
            interrupt_timeout=0.0000,
        )
    except Exception:
        if not CI and execution_group.experimental:
            session.warn(
                "Pyright failed but the session was marked as experimental, exiting with 0"
            )
        else:
            raise


@nox.session(name="pyright-cli", default=False, python=None, venv_backend="none")
def pyright_cli(session: nox.Session) -> None:
    """Serves as a runner for running specific pyright sessions."""
    if not session.interactive:
        session.error("pyright-cli can only be run interactively.")
    # filter down to just the min python, max python, and the speciality directories
    forced_python = session.python
    paths_covered: Dict[str, Set[str]] = {}
    for group in get_groups_for_session("pyright"):
        if group.python not in paths_covered:
            paths_covered[group.python] = set()
        if paths_covered[group.python].issuperset(set(group.pyright_paths)):
            continue
        if (
            paths_covered.get(MIN_PYTHON)
            and paths_covered[MIN_PYTHON].issuperset(set(group.pyright_paths))
            and group.python != SUPPORTED_PYTHONS[-1]
        ):
            continue
        if forced_python and group.python != forced_python:
            continue
        paths_covered[group.python].update(group.pyright_paths)
        paths = session.posargs
        if not paths or (paths := check_paths(session, session.posargs, group)):
            session.log(f"Running pyright({group.pyright_session_id})")
            session.notify(
                f"pyright({group.pyright_session_id})",
                paths or group.pyright_paths,
            )


@nox.session()
@nox.parametrize(
    ("python", "execution_group"),
    [(group.python, group) for group in get_groups_for_session("test")],
    ids=[group.test_session_id for group in get_groups_for_session("test")],
    tags=[group.tags.get("test", []) for group in get_groups_for_session("test")],
)
def test(session: nox.Session, execution_group: ExecutionGroup) -> None:
    """Run tests."""
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


@nox.session(tags=("ci", "test"))
def coverage(session: nox.Session) -> None:
    """Display coverage information from the tests."""
    install_deps(session)

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
