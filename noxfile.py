from typing import List, Optional

import nox

nox.options.error_on_external_run = True
nox.options.sessions = [
    "lint",
    "pyright",
    "tests",
]
nox.needs_version = ">=2022.1.7"


GENERAL_REQUIREMENTS = ["taskipy~=1.10.1", "python-dotenv[cli]~=0.19.2"]

LINT_REQUIREMENTS = [
    "pre-commit~=2.17.0",
]

PYRIGHT_REQUIREMENTS = [
    "pyright==1.1.244",
    "mypy",  # needed to typecheck the mypy plugin with pyright
]

PYRIGHT_ENV = {
    "PYRIGHT_PYTHON_IGNORE_WARNINGS": "1",
}
TEST_REQUIREMENTS = [
    "pytest~=7.1.2",
    "pytest-cov~=3.0.0",
    "pytest-asyncio~=0.18.3",
    "looptime~=0.2",
]

ALL_REQUIREMENTS = [
    *GENERAL_REQUIREMENTS,
    *LINT_REQUIREMENTS,
    *PYRIGHT_REQUIREMENTS,
    *TEST_REQUIREMENTS,
]


@nox.session()
def docs(session: nox.Session):
    """Build and generate the documentation.

    If running locally, will build automatic reloading docs.
    If running in CI, will build a production version of the documentation.
    """
    session.install("-e", ".[docs]")
    with session.chdir("docs"):
        args = ["-b", "html", "-j", "auto", "-n", ".", "_build/html"]
        if session.interactive:
            session.install("sphinx-autobuild==2021.3.14")
            session.run(
                "sphinx-autobuild",
                "--ignore",
                "_build",
                "--watch",
                "../disnake",
                "--port",
                "8009",
                *args,
            )
        else:
            session.run(
                "sphinx-build",
                "-aE",
                *args,
            )


@nox.session(reuse_venv=True)
def lint(session: nox.Session):
    """Check all files for linting errors"""
    session.install(*LINT_REQUIREMENTS)
    session.run("pre-commit", "run", "--all-files")


@nox.session(reuse_venv=True)
def slotscheck(session: nox.Session):
    """Run slotscheck."""
    session.install("-e", ".")
    session.install("slotscheck~=0.13.0")
    session.run("python", "-m", "slotscheck", "--verbose", "-m", "disnake")


@nox.session(reuse_venv=True)
def pyright(session: nox.Session):
    """Run pyright."""
    session.install("-e", ".[docs,speed,voice]")
    session.install(*PYRIGHT_REQUIREMENTS)
    try:
        session.run("python", "-m", "pyright", *session.posargs, env=PYRIGHT_ENV)
    except KeyboardInterrupt:
        pass


@nox.session(reuse_venv=True)
@nox.parametrize("extras", [None, "speed", "voice"])
def tests(session: nox.Session, extras: Optional[str]):
    """Run tests."""
    if extras:
        session.install("-e", f".[{extras}]")
    else:
        session.install("-e", ".")
    session.install(*TEST_REQUIREMENTS)
    # todo: only run tests that depend on the different dependencies
    session.run("pytest", "-v", "--cov", "--cov-report=term", "--cov-append", "--cov-context=test")
    session.notify("coverage", session.posargs)


@nox.session(reuse_venv=True)
def coverage(session: nox.Session):
    """Display coverage information from the tests."""
    session.install("coverage[toml]~=6.3.2")
    if "html" in session.posargs or "serve" in session.posargs:
        session.run("coverage", "html", "--show-contexts")
    if "serve" in session.posargs:
        session.run(
            "python", "-m", "http.server", "8009", "--directory", "htmlcov", "--bind", "127.0.0.1"
        )
    if "erase" in session.posargs:
        session.run("coverage", "erase")


@nox.session(python=False)
def setup(session: nox.Session):
    """Set up the local environment."""
    session.log("Installing dependencies to the global environment.")

    if session.posargs:
        posargs = session.posargs[:]
    else:
        posargs = [
            "lint",
            "tests",
            "docs",
        ]

    deps: List[str] = [".", *GENERAL_REQUIREMENTS]
    if "lint" in posargs:
        deps.extend([*LINT_REQUIREMENTS, *PYRIGHT_REQUIREMENTS, "slotscheck~=0.13.0"])

    if "docs" in posargs:
        deps.remove(".")
        deps.insert(0, ".[docs]")

    if "tests" in posargs:
        deps.extend(TEST_REQUIREMENTS)

    session.run("python", "-m", "pip", "install", "-U", *deps)

    if "lint" in posargs:
        session.run("pre-commit", "install", "--install-hooks")
