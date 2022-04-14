.. currentmodule:: disnake

.. _ext_commands_slash_commands:

Slash Commands
==============

Slash commands can significantly simplify the user's experience with your bot. Once "/" is pressed on the keyboard,
the list of slash commands appears. You can fill the options and read the hints at the same time, while types are validated
instantly. This library allows to make such commands in several minutes, regardless of their complexity.

.. _slash_commands_start:

Getting started
---------------

You have probably noticed that slash commands have really interactive user interface, as if each slash command was built-in.
This is because each slash command is registered in Discord before people can see it. This library handles registration for you,
but you can still manage it.

By default, the registration is global. This means that your slash commands will be visible everywhere, including bot DMs.
Global registration can take up to 1 hour to complete, this is an API limitation. You can change the registration to be local,
so your slash commands will only be visible in several guilds. This type of registration is almost instant.

This code sample shows how to set the registration to be local:

.. code-block:: python3

    from disnake.ext import commands

    bot = commands.Bot(
        command_prefix='!',
        test_guilds=[123456789],
        # In the list above you can specify the IDs of your test guilds.
        # Why is this kwarg called test_guilds? This is because you're not meant to use
        # local registration in production, since you may exceed the rate limits.
    )

For global registration, don't specify this parameter.

Another useful parameter is ``sync_commands_debug``. If set to ``True``, you receive debug messages related to the
app command registration by default, without having to change the log level of any loggers
(see :class:`Bot.sync_commands_debug <ext.commands.Bot.sync_commands_debug>` for more info).
This is useful if you want to figure out some registration details:

.. code-block:: python3

    from disnake.ext import commands

    bot = commands.Bot(
        command_prefix='!',
        test_guilds=[123456789], # Optional
        sync_commands_debug=True
    )

If you want to disable the automatic registration, set ``sync_commands`` to ``False``:

.. code-block:: python3

    from disnake.ext import commands

    bot = commands.Bot(
        command_prefix='!',
        sync_commands=False
    )

Basic Slash Command
-------------------

Make sure that you've read :ref:`slash_commands_start`, it contains important information about command registration.

Here's an example of a slash command:

.. code-block:: python3

    @bot.slash_command(description="Responds with 'World'")
    async def hello(inter):
        await inter.response.send_message("World")

A slash command must always have at least one parameter, ``inter``, which is the :class:`.ApplicationCommandInteraction` as the first one.

I can't see my slash command, what do I do? Read :ref:`slash_commands_start`.

.. _param_syntax:

Parameters
----------

You may want to define a couple of options for your slash command. In disnake, the definition of options is based on annotations.

Here's an example of a command with one integer option (without a description):

.. code-block:: python3

    @bot.slash_command(description="Multiplies the number by 7")
    async def multiply(inter, number: int):
        await inter.response.send_message(number * 7)

The result should look like this:

.. image:: /images/app_commands/int_option.png

You can of course set a default for your option by giving a default value:

.. code-block:: python3

    @bot.slash_command(description="Multiplies the number by a multiplier")
    async def multiply(inter, number: int, multiplier: int = 7):
        await inter.response.send_message(number * multiplier)

You may have as many options as you want but the order matters, an optional option cannot be followed by a required one.

Option Types
++++++++++++

You might already be familiar with discord.py's converters, slash commands have a very similar equivalent in the form of option types.
Discord itself supports only a few built-in types which are guaranteed to be enforced:

- :class:`str`
- :class:`int`
- :class:`float`
- :class:`bool`
- :class:`disnake.User` or :class:`disnake.Member`
- :class:`disnake.abc.GuildChannel`\*
- :class:`disnake.Role`\*\*
- :class:`disnake.Attachment`

All the other types may be converted implicitly, similarly to :ref:`ext_commands_basic_converters`

.. code-block:: python3

    @bot.slash_command()
    async def multiply(
        interaction,
        string: str,
        integer: int,
        number: float,
        user: disnake.User,
        emoji: disnake.Emoji,
        message: disnake.Message
    ):
        ...

.. note::
  \* All channel subclasses and unions are also supported. See :attr:`.ParamInfo.channel_types` for more fine-grained control

  \*\* Role and Member may be used together to create a "mentionable" (``Union[Role, Member]``)


.. _param_ranges:

Number Ranges
+++++++++++++

:class:`int` and :class:`float` parameters support minimum and maximum allowed
values using the ``lt``, ``le``, ``gt``, ``ge`` parameters on :func:`Param <ext.commands.Param>`.
For instance, you could restrict an option to only accept positive integers:

.. code-block:: python3

    @bot.slash_command()
    async def command(
        inter: disnake.ApplicationCommandInteraction,
        amount: int = commands.Param(gt=0),
    ):
        ...


Instead of using :func:`Param <ext.commands.Param>`, you can also use a :class:`Range` annotation.
The range bounds are both inclusive; using ``...`` as a bound indicates that this end of the range is unbounded.
The type of the option is determined by the range bounds, with the option being a
:class:`float` if at least one of the bounds is a :class:`float`, and :class:`int` otherwise.

.. code-block:: python3

    @bot.slash_command()
    async def ranges(
        inter: disnake.ApplicationCommandInteraction,
        a: commands.Range[0, 10],       # 0 - 10 int
        b: commands.Range[0, 10.0],     # 0 - 10 float
        c: commands.Range[1, ...],      # positive int
    ):
        ...

.. note::

    Type checker support for :class:`Range` is limited. Pylance/Pyright seem to handle it correctly;
    MyPy currently needs a plugin for it to understand :class:`Range` semantics, which can be added in
    the configuration file (``setup.cfg``, ``mypy.ini``):

    .. code-block:: ini

        [mypy]
        plugins = disnake.ext.mypy_plugin

    For ``pyproject.toml`` configs, use this instead:

    .. code-block:: toml

        [tool.mypy]
        plugins = "disnake.ext.mypy_plugin"


Docstrings
----------

If you have a feeling that option descriptions make the parameters of your function look overloaded, use docstrings.
This feature allows to describe your command and options in triple quotes inside the function, following the RST markdown.

In order to describe the parameters, list them under the ``Parameters`` header, underlined with dashes:

.. code-block:: python3

    @bot.slash_command()
    async def give_cookies(
        inter: disnake.ApplicationCommandInteraction,
        user: disnake.User,
        amount: int = 1
    ):
        """
        Give several cookies to a user

        Parameters
        ----------
        user: The user to give cookies to
        amount: The amount of cookies to give
        """
        ...

.. note ::
    In the above example we're using a simplified RST markdown.

If you prefer the real RST format, you can still use it:

.. code-block:: python3

    @bot.slash_command()
    async def give_cookies(
        inter: disnake.ApplicationCommandInteraction,
        user: disnake.User,
        amount: int = 1
    ):
        """
        Give several cookies to a user

        Parameters
        ----------
        user: :class:`disnake.User`
            The user to give cookies to
        amount: :class:`int`
            The amount of cookies to give
        """
        ...


Parameter Descriptors
+++++++++++++++++++++

Python has no truly *clean* way to provide metadata for parameters, so disnake uses the same approach as fastapi using
parameter defaults. At the current time there's only :class:`~disnake.ext.commands.Param`.

With this you may set the name, description, custom converters, :ref:`autocompleters`, and more.

.. code-block:: python3

    @bot.slash_command()
    async def math(
        interaction: disnake.ApplicationCommandInteraction,
        a: int = commands.Param(le=10),
        b: int = commands.Param(le=10),
        op: str = commands.Param(name="operator", choices=["+", "-", "/", "*"])
    ):
        """
        Perform an operation on two numbers as long as both of them are less than or equal to 10
        """
        ...

.. code-block:: python3

    @bot.slash_command()
    async def multiply(
        interaction: disnake.ApplicationCommandInteraction,
        clean: str = commands.Param(converter=lambda inter, arg: arg.replace("@", "\\@")
    ):
        ...


.. note ::
    The converter parameter only ever takes in a **function**, not a Converter class.
    Converter classes are completely unusable in disnake due to their inconsistent typing.

.. _option_choices:

Choices
-------

Some options can have a list of choices, so the user doesn't have to manually fill the value.
The most elegant way of defining the choices is by using enums. These enums **must** inherit from the type of their value if you want them to work with linters.

For example:

.. code-block:: python3

    from enum import Enum

    class Animal(str, Enum):
        Dog = 'dog'
        Cat = 'cat'
        Penguin = 'peng'

    @bot.slash_command()
    async def blep(inter: disnake.ApplicationCommandInteraction, animal: Animal):
        await inter.response.send_message(animal)

.. note ::
    The ``animal`` arg will receive one of the enum values.

You can define an enum in one line:

.. code-block:: python3

    Animal = commands.option_enum({"Dog": "dog", "Cat": "cat", "Penguin": "penguin"})

    @bot.slash_command()
    async def blep(inter: disnake.ApplicationCommandInteraction, animal: Animal):
        await inter.response.send_message(animal)

Or even forget about values and define the enum from list:

.. code-block:: python3

    Animal = commands.option_enum(["Dog", "Cat", "Penguin"])

    @bot.slash_command()
    async def blep(inter: disnake.ApplicationCommandInteraction, animal: Animal):
        await inter.response.send_message(animal)

Or you can simply list the choices in ``commands.Param``:

.. code-block:: python3

    @bot.slash_command()
    async def blep(
        inter: disnake.ApplicationCommandInteraction,
        animal: str = commands.Param(choices={"Dog": "dog", "Cat": "cat", "Penguin": "penguin"})
    ):
        await inter.response.send_message(animal)

    # Or define the choices in a list

    @bot.slash_command()
    async def blep(
        inter: disnake.ApplicationCommandInteraction,
        animal: str = commands.Param(choices=["Dog", "Cat", "Penguin"])
    ):
        await inter.response.send_message(animal)

.. _autocompleters:

Autocompleters
--------------

Slash commands support interactive autocompletion. You can define a function that will constantly suggest autocomplete options
while the user is typing. So basically autocompletion is roughly equivalent to dynamic choices.

In order to build an option with autocompletion, define a function that takes 2 parameters - :class:`.ApplicationCommandInteraction` instance,
representing an autocomp interaction with your command, and a :class:`str` instance, representing the current user input. The function
should return a list of strings or a mapping of choice names to values.

For example:

.. code-block:: python3

    LANGUAGES = ["python", "javascript", "typescript", "java", "rust", "lisp", "elixir"]

    async def autocomp_langs(inter: disnake.ApplicationCommandInteraction, user_input: str):
        return [lang for lang in LANGUAGES if user_input.lower() in lang]

    @bot.slash_command()
    async def example(
        inter: disnake.ApplicationCommandInteraction,
        language: str = commands.Param(autocomplete=autocomp_langs)
    ):
        ...


In case you need don't want to use :class:`Param <ext.commands.Param>` or need to use ``self`` in a cog you may
create autocomplete options with the :func:`autocomplete <ext.commands.InvokableSlashCommand.autocomplete>` decorator:

.. code-block:: python3

    @bot.slash_command()
    async def languages(inter: disnake.CommandInteraction, language: str):
        pass


    @languages.autocomplete("language")
    async def language_autocomp(inter: disnake.CommandInteraction, string: str):
        string = string.lower()
        return [lang for lang in LANGUAGES if string in lang.lower()]
        ...

Subcommands And Groups
----------------------

Groups of commands work differently in terms of slash commands. Instead of defining a group, you should still define a slash command
and then nest some sub-commands or sub-command-groups there via special decorators.

For example, here's how you make a ``/show user`` command:

.. code-block:: python3

    @bot.slash_command()
    async def show(inter):
        # Here you can paste some code, it will run for every invoked sub-command.
        pass

    @show.sub_command()
    async def user(inter, user: disnake.User):
        """
        Description of the subcommand

        Parameters
        ----------
        user: Enter the user to inspect
        """
        ...

.. note ::
    After being registered this command will be visible as ``/show user`` in the list, not allowing you to invoke ``/show`` without
    any sub-commands. This is an API limitation.

You can implement double nesting and build commands like ``/parent group subcmd``:

.. code-block:: python3

    @bot.slash_command()
    async def parent(inter):
        pass

    @parent.sub_command_group()
    async def group(inter):
        pass

    @group.sub_command()
    async def subcmd(inter):
        # Some stuff
        pass

.. note ::
    This is the deepest nesting available.

Injections
----------

We have them, look at `this example <https://github.com/DisnakeDev/disnake/blob/master/examples/slash_commands/injections.py>`_ for more information ✨
