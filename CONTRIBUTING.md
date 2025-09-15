<!-- SPDX-License-Identifier: MIT -->

# Contributing to disnake

First off, thanks for taking the time to contribute! It makes the library substantially better. :tada:

The following is a set of guidelines for contributing to the repository. These are not necessarily hard rules, but they streamline the process for everyone involved.

## Table of Contents

- [Table of Contents](#table-of-contents)
- [This is too much to read! I want to ask a question!](#this-is-too-much-to-read-i-want-to-ask-a-question)
- [Good Bug Reports](#good-bug-reports)
- [Creating a Pull Request](#creating-a-pull-request)
  - [Overview](#overview)
  - [Initial setup](#initial-setup)
  - [Commit/PR Naming Guidelines](#commitpr-naming-guidelines)
  - [Formatting](#formatting)
  - [Pyright](#pyright)
  - [Changelogs](#changelogs)
  - [Documentation](#documentation)
- [Migrating development environments](#migrating-development-environments)
  - [Migrating `pdm`'s scripts to `nox`](#migrating-pdms-scripts-to-nox)

## This is too much to read! I want to ask a question!

> [!IMPORTANT]
> Please try your best not to create new issues in the issue tracker just to ask questions, unless they provide value to a larger audience.

Generally speaking, questions are better suited in our resources below.

- The official Discord server: <https://discord.gg/disnake>
- The [FAQ in the documentation](https://docs.disnake.dev/en/latest/faq.html)
- The project's [discussions section](https://github.com/DisnakeDev/disnake/discussions)

---

## Good Bug Reports

To report bugs (or to suggest new features), visit our [issue tracker](https://github.com/DisnakeDev/disnake/issues).
The issue templates will generally walk you through the steps, but please be aware of the following things:

1. **Don't open duplicate issues**. Before you submit an issue, search the issue tracker to see if an issue for your problem already exists. If you find a similar issue, you can add a comment with additional information or context to help us understand the problem better.
2. **Include the *complete* traceback** when filing a bug report about exceptions or tracebacks. Without the complete traceback, it will be much more difficult for others to understand (and perhaps fix) your issue.
3. **Add a minimal reproducible code snippet** that results in the behavior you're seeing. This helps us quickly confirm a bug or point out a solution to your problem. We cannot reliably investigate bugs without a way to reproduce them.

If the bug report is missing this information, it'll take us longer to fix the issue. We may ask for clarification, and if no response was given, the issue will be closed.

---

## Creating a Pull Request

Creating a pull request is fairly straightforward. Make sure it focuses on a single aspect and avoids scope creep, then it's probably good to go.

If you're unsure about some aspect of development, feel free to use existing files as a guide or reach out via the Discord server.

### Overview

The general workflow can be summarized as follows:

1. Fork + clone the repository.
2. Initialize the development environment: `pdm run nox -s dev`.
3. Create a new branch.
4. Commit your changes, update documentation if required.
5. Add a changelog entry (e.g. `changelog/1234.feature.rst`).
6. Push the branch to your fork, and [submit a pull request!](https://github.com/DisnakeDev/disnake/compare)

Specific development aspects are further explained below.

### Initial setup

We use [PDM](https://pdm-project.org/) as our dependency manager. If it isn't already installed on your system, you can follow the installation steps [from PDM](https://pdm-project.org/latest/#installation) to get started.

Once PDM is installed, use the following command to initialize a virtual environment, install the necessary development dependencies, and install the [`pre-commit`](#formatting) hooks.

```sh
$ pdm run setup_env
```

This will:

- create `pdm.lock`
- create a venv at `.venv`
- install all dependences to `.venv`
- install pre-commit hooks at `.git/hooks/pre-commit`

Other tools used in this project include [ruff](https://docs.astral.sh/ruff) (formatter and linter), and [pyright](https://microsoft.github.io/pyright/#/) (type-checker). For the most part, these automatically run on every commit with no additional action required - see below for details.

All of the following checks also automatically run for every PR on GitHub, so don't worry if you're not sure whether you missed anything. A PR cannot be merged as long as there are any failing checks.

### Commit/PR Naming Guidelines

This project uses the commonly known [conventional commit format](https://www.conventionalcommits.org/en/v1.0.0/).
While not necessarily required (but appreciated) for individual commit messages, please make sure to title your PR according to this schema:

```
<type>(<scope>)<!>: <short summary>
  │       │     │         │
  │       │     │         └─⫸ Summary in present tense, not capitalized, no period at the end
  │       │     │
  │       │     └─⫸ [optional] `!` indicates a breaking change
  │       │
  │       └─⫸ [optional] Commit Scope: The affected area, e.g. gateway, user, ...
  │
  └─⫸ Commit Type: feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert
```

Examples: `feat: support new avatar format` or `fix(gateway): use correct url for resuming connection`.  
Details about the specific commit types can be found on the [conventional commits documentation](https://github.com/commitizen/conventional-commit-types/blob/master/index.json).

### Formatting

This project follows PEP-8 guidelines (mostly) with a column limit of 100 characters, and uses the tools mentioned above to enforce a consistent coding style.

The installed [`pre-commit`](https://pre-commit.com/) hooks will automatically run before every commit, which will format/lint the code
to match the project's style. Note that you will have to stage and commit again if anything was updated!  
Most of the time, running pre-commit will automatically fix any issues that arise.

### Pyright

For type-checking, run `pdm run nox -s pyright` (append `-- -w` to have it automatically re-check on every file change).
> [!NOTE]
> If you're using VSCode and pylance, it will use the same type-checking settings, which generally means that you don't necessarily have to run `pyright` separately.  
> However, since we use a specific version of `pyright` (which may not match pylance's version), there can be version differences which may lead to different results.

### Changelogs

We use [towncrier](https://github.com/twisted/towncrier) for managing our changelogs. Each change is required to have at least one file in the [`changelog/`](changelog/README.rst) directory, unless it's a trivial change. There is more documentation in that directory on how to create a changelog entry.

### Documentation

We use Sphinx to build the project's documentation, which includes [automatically generating](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html) the API Reference from docstrings using the [NumPy style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_numpy.html).  
To build the documentation locally, use `pdm run nox -s docs` and visit <http://127.0.0.1:8009/> once built.

Changes should be marked with a [version directive](https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#describing-changes-between-versions) as documented on the Sphinx documentation.

For the `version` argument, provide ``|vnext|`` as the argument.
We have a custom role which replaces ``|vnext|`` with the next version of the library upon building the documentation.

## Migrating development environments

### Migrating `pdm`'s scripts to `nox`

Previously, we were using pdm's scripts functions as a simple caller for our nox scripts.
We are migrating to using nox directly, the tasks now look like the following:

```sh
$ pdm docs  
$ pdm lint  
$ pdm pyright  
$ pdm test  
$ pdm setup_env
```

Becomes:

```sh
$ pdm run nox -s docs
$ pdm run nox -s lint
$ pdm run nox -s pyright
$ pdm run nox -s test
$ pdm run noxfile.py -s dev
```

`nox` may also be installed to your path using either [uv](https://docs.astral.sh/uv) or [pipx](https://pipx.pypa.io) and used on the root: eg `nox -s docs` with no preceding `pdm run`

```sh
# without global nox
$ pdm run noxfile.py -s dev

# with global nox
$ pipx install nox
$ nox -s dev
```

> [!TIP]
> To provide arguments to the selected sessions with `nox`, pass them **after** `--`. For example, to tell `pre-commit` to only run `ruff format`, run `nox -s lint -- ruff-format`.
