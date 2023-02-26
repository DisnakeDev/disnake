<!-- SPDX-License-Identifier: MIT -->

# Contributing to disnake

- [Bug Reports](#good-bug-reports)
- [Creating Pull Requests](#creating-a-pull-request)

First off, thanks for taking the time to contribute. It makes the library substantially better. :+1:

The following is a set of guidelines for contributing to the repository. These are mostly guidelines, not hard rules.


## This is too much to read! I want to ask a question!

Generally speaking questions are better suited in our resources below.

- The official support server: https://discord.gg/disnake
- The [FAQ in the documentation](https://docs.disnake.dev/en/latest/faq.html)
- The project's [discussions section](https://github.com/DisnakeDev/disnake/discussions)

Please try your best not to create new issues in the issue tracker just to ask questions. Most of them don't belong there unless they provide value to a larger audience.

---

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

---

## Creating a Pull Request

Creating a pull request is fairly simple, just make sure it focuses on a single aspect and doesn't manage to have scope creep and it's probably good to go.

### Formatting

We would greatly appreciate the code submitted to be of a consistent style with other code in disnake. This project follows PEP-8 guidelines (mostly) with a column limit of 100 characters.


We use [`PDM`](https://pdm.fming.dev/) for development. If PDM is not already installed on your system, you can follow their [installation steps here](https://pdm.fming.dev/latest/#installation) to get started.

Once PDM is installed and avaliable, use the following command to initialise a virtual environment, install the necessary development dependencies, and install the [`pre-commit`](https://pre-commit.com/#quick-start) hooks.
.
```
pdm run setup_env
```

The installed `pre-commit` hooks will automatically run before every commit, which will format/lint the code
to match the project's style. Note that you will have to stage and commit again if anything was updated!

Most of the time, running pre-commit will automatically fix any issues that arise, but this is not always the case.
We have a few hooks that *don't* resolve their issues automatically, and must be fixed manually.
One of these is the license header, which must exist in all files unless comments are not supported in those files, or they
are not text files, in which case exceptions can be made. These headers must exist following the format
documented at [https://spdx.dev/ids/](https://spdx.dev/ids/).


### Scripts

To run all important checks and tests, use `pdm run nox`:
```sh
pdm run nox -R
```

You can also choose to only run a single task; run `pdm run --list` to view all available scripts and use `pdm run <name>` to run them.

Some notes (all of the mentioned scripts are automatically run by `pdm run nox -R`, see above):
- If `pre-commit` hooks aren't installed, run `pdm run lint` manually to check and fix the formatting in all files.  
  **Note**: If the code is formatted incorrectly, `pre-commit` will apply fixes and exit without committing the changes - just stage and commit again.
- For type-checking, run `pdm run pyright`. You can use `pdm run pyright -w` to automatically re-check on every file change.  
  **Note**: If you're using VSCode and pylance, it will use the same type-checking settings, which generally means that you don't necessarily have to run `pyright` separately. However, there can be version differences which may lead to different results when later run in CI on GitHub.
- Tests can be run using `pdm run test`. If you changed some functionality, you may have to adjust a few tests - if you added new features, it would be great if you added new tests for them as well.

A PR cannot be merged as long as there are any failing checks.

### Changelogs

We use [towncrier](https://github.com/twisted/towncrier) for managing our changelogs. Each change is required to have at least one file in the [`changelog/`](changelog/README.rst) directory. There is more documentation in that directory on how to create a changelog entry.

### Git Commit Guidelines

- Use present tense (e.g. "Add feature" not "Added feature")
- Reference issues or pull requests outside of the first line.
    - Please use the shorthand `#123` and not the full URL.

If you do not meet any of these guidelines, don't fret. Chances are they will be fixed upon rebasing but please do try to meet them to remove some of the workload.

---

## How do I add a new feature?

Welcome! If you've made it to this point you are likely a new contributor! This section will go through how to add a new feature to disnake.

Most attributes and data structures are broken up in to a file for each related class. For example, `disnake.Guild` is defined in [disnake/guild.py](disnake/guild.py), and `disnake.GuildPreview` is defined in [disnake/guild_preview.py](disnake/guild_preview.py). For example, writing a new feature to `disnake.Guild` would go in [disnake/guild.py](disnake/guild.py), as part of the `disnake.Guild` class.

### Adding a new API Feature

However, adding a new feature that interfaces with the API requires also updating the [disnake/types](disnake/types) directory to match the relevant [API specifications](https://discord.com/developers/docs). We ask that when making or receiving payloads from the API, they are typed and typehints are used on the functions that are processing said data. For example, take a look at `disnake.abc.Messageable.pins` (defined in [disnake/abc.py](disnake/abc.py)).


```py
    async def pins(self) -> List[Message]:
        channel = await self._get_channel()
        state = self._state
        data = await state.http.pins_from(channel.id)
        return [state.create_message(channel=channel, data=m) for m in data]
```
*docstring removed for brevity*

Here we have several things occuring. First, we have annotated the return type of this method to return a list of `Message`s. As disnake supports Python 3.8, we use typing imports instead of subscripting built-ins — hence the capital ``List``.

The next interesting thing is `self._state`. The library uses a state-centric design, which means the state is passed around to most objects.
Every Discord model that makes requests uses that internal state and its `http` attribute to make requests to the Discord API. Each endpoint is processed and defined in [disnake/http.py](disnake/http.py) — and it's where `http.pins_from` is defined too, which looks like this:

```py
    def pins_from(self, channel_id: Snowflake) -> Response[List[message.Message]]:
        return self.request(Route("GET", "/channels/{channel_id}/pins", channel_id=channel_id))
```

This is the basic model that all API request methods follow. Define the `Route`, provide the major parameters (in this example `channel_id`), then return a call to `self.request()`.

The `Response[]` part in the typehint is referring to `self.request`, as the important thing here is that `pins_from` is **not** a coroutine. Rather, `pins_from` does preprocessing and `self.request` does the actual work. The result from `pins_from` is awaited by `disnake.abc.Messageable.pins`.

The Route class is how all routes are processed internally. Along with `self.request`, this makes it possible to properly handle all ratelimits. This is why `channel_id` is provided as a kwarg to `Route`, as it is considered a major parameter for ratelimit handling.

#### Writing Documentation

While a new feature can be useful, it requires documentation to be usable by everyone. When updating a class or method, we ask that you use
[Sphinx directives](https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-versionadded) in the docstring to note when it was added or updated, and what about it was updated.

For example, here is the docstring for `pins()`:

```py
      """|coro|

      Retrieves all messages that are currently pinned in the channel.

      .. note::

          Due to a limitation with the Discord API, the :class:`.Message`
          objects returned by this method do not contain complete
          :attr:`.Message.reactions` data.

      Raises
      ------
      HTTPException
          Retrieving the pinned messages failed.

      Returns
      -------
      List[:class:`.Message`]
          The messages that are currently pinned.
      """
```

If we were to add a new parameter to this method, a few things would need to be added to this docstring. Lets pretend we're adding a parameter, ``oldest_first``.

We use NumPy style docstrings parsed with Sphinx's Napoleon extension — the primary documentation for these docstrings can be found [here](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html).

```py
      """
      ...

      Parameters
      ----------
      oldest_first: bool
          Whether to order the result by the oldest or newest pins first.

          .. versionadded:: 2.9

      ...
      """
```

It is important that the section header comes **after** any description and admonitions that exist, as it will stop the parsing of the description.

The end result of these changes would be as follows:

```py
      """|coro|

      Retrieves all messages that are currently pinned in the channel.

      .. note::

          Due to a limitation with the Discord API, the :class:`.Message`
          objects returned by this method do not contain complete
          :attr:`.Message.reactions` data.

      Parameters
      ----------
      oldest_first: bool
          Whether to order the result by the oldest or newest pins first.

          .. versionadded:: 2.9

      Raises
      ------
      HTTPException
          Retrieving the pinned messages failed.

      Returns
      -------
      List[:class:`.Message`]
          The messages that are currently pinned.
      """
  ```

*If you're having trouble with adding or modifying documentation, don't be afraid to reach out!
We understand that the documentation can be intimidating, and there are quite a few quirks and limitations to be aware of.*
