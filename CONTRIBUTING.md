## Contributing to disnake

First off, thanks for taking the time to contribute. It makes the library substantially better. :+1:

The following is a set of guidelines for contributing to the repository. These are mostly guidelines, not hard rules.


## This is too much to read! I want to ask a question!

Generally speaking questions are better suited in our resources below.

- The official support server: https://discord.gg/disnake
- The [FAQ in the documentation](https://docs.disnake.dev/en/latest/faq.html)
- The project's [discussions section](https://github.com/DisnakeDev/disnake/discussions)

Please try your best not to create new issues in the issue tracker just to ask questions. Most of them don't belong there unless they provide value to a larger audience.


## Good Bug Reports

Please be aware of the following things when filing bug reports.

1. Don't open duplicate issues. Please search your issue to see if it has been asked already. Duplicate issues will be closed.
2. When filing a bug about exceptions or tracebacks, please include the *complete* traceback. Without the complete traceback the issue might be **unsolvable** and you will be asked to provide more information.
3. Make sure to provide enough information to make the issue workable. The issue template will generally walk you through the process but they are enumerated here as well:
    - A **summary** of your bug report. This is generally a quick sentence or two to describe the issue in human terms.
    - Guidance on **how to reproduce the issue**. Ideally, this should have a small code sample that allows us to run and see the issue for ourselves to debug. **Please make sure that the token is not displayed**. If you cannot provide a code snippet, then let us know what the steps were, how often it happens, etc.
    - Tell us **what you expected to happen**. That way we can meet that expectation.
    - Tell us **what actually happens**. What ends up happening in reality? It's not helpful to say "it fails" or "it doesn't work". Say *how* it failed, do you get an exception? Does it hang? How are the expectations different from reality?
    - Tell us **information about your environment**. What version of disnake are you using? How was it installed? What operating system are you running on? These are valuable questions and information that we use.

If the bug report is missing this information then it'll take us longer to fix the issue. We will probably ask for clarification, and barring that if no response was given then the issue will be closed.


## Submitting a Pull Request

Submitting a pull request is fairly simple, just make sure it focuses on a single aspect and doesn't manage to have scope creep and it's probably good to go. It would be incredibly lovely if the style is consistent to that found in the project. This project follows PEP-8 guidelines (mostly) with a column limit of 100 characters.

We use [`nox`](https://nox.thea.codes/en/stable/) for automating development tasks. Run these commands to
install `nox` and `taskipy` as well as the required dependencies in your environment,
and to set up [`pre-commit`](https://pre-commit.com/#quick-start) hooks.  
Make sure you have a virtualenv activated if you don't want it to install the packages globally!
```
pip install nox taskipy
task setup_env
```

The installed `pre-commit` hooks will automatically run before every commit, which will format/lint the code
to match the project's style. Note that you will have to stage and commit again if anything was updated!


### Tasks

**tl;dr:**  
To run all important checks and tests, use `nox`:
```sh
nox -R
```

You can also choose to only run a single task; run `task --list` to view all available tasks and use `task <name>` to run them.

Some notes (all of the mentioned tasks are automatically run by `nox -R`, see above):
- If `pre-commit` hooks aren't installed, run `task lint` manually to check and fix the formatting in all files.  
  **Note**: If the code is formatted incorrectly, `pre-commit` will apply fixes and exit without committing the changes - just stage and commit again.
- For type-checking, run `task pyright`. You can use `task pyright -w` to automatically re-check on every file change.  
  **Note**: If you're using VSCode and pylance, it will use the same type-checking settings, which generally means that you don't necessarily have to run `pyright` separately. However, there can be version differences which may lead to different results when later run in CI on GitHub.
- Tests can be run using `task test`. If you changed some functionality, you may have to adjust a few tests - if you added new features, it would be great if you added new tests for them as well.

A PR cannot be merged as long as there are any failing tasks.


### Git Commit Guidelines

- Use present tense (e.g. "Add feature" not "Added feature")
- Reference issues or pull requests outside of the first line.
    - Please use the shorthand `#123` and not the full URL.

If you do not meet any of these guidelines, don't fret. Chances are they will be fixed upon rebasing but please do try to meet them to remove some of the workload.
