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
app command registration. This is useful if you want to figure out some registration details:

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

All the other types may be converted implicitly, similarly to :ref:`discord_converters`

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
  \* All channel subclasses and unions are also supported, see :ref:`channel_types`

  \*\* Role and Member may be used together to create a "mentionable" (:class:`Union[Role, Member]`)

Parameter Descriptors
+++++++++++++++++++++

Python has no truly *clean* way to provide metadata for parameters, so disnake uses the same approach as fastapi using
parameter defaults. At the current time there's only :class:`Param`.

With this you may set the name, description, custom converters and :ref:`autocompleters`.

.. code-block:: python3

    @bot.slash_command()
    async def multiply(
        interaction: commands.ApplicationCommandInteraction,
        a: int = commands.Param(description="The first number"),
        b: int = commands.Param(description="The second number"),
        op: str = commands.Param(name="operator", description="The operator")
    ):
        ...

.. code-block:: python3

    @bot.slash_command()
    async def multiply(
        interaction: commands.ApplicationCommandInteraction,
        clean: str = commands.Param(converter=lambda inter, arg: arg.replace("@", "\\@")
    ):
        ...

.. note ::
    There is a possibility that your editor is going to complain about the usage of ``commands.Param``.
    This is due to the limitation of most linters which forbid using incorrect types as function defaults.
    In that case use the lowercase alias ``commands.param``

    All keyword arguments of :class:`Param` have shorter aliases:
        - ``description`` -> ``desc``
        - ``converter`` -> ``conv``
        - ``autocomplete`` -> ``autocomp``


.. note ::
    The converter parameter only ever takes in a **function**, not a Converter class.
    Converter classes are completely unusable in disnake due to their inconsistent typing.

.. _autocompleters:


Choices
-------
Just enums n stuff. [Not finished]

Autocompleters
--------------
Use the ``autocompleter`` kwarg. [Not finished]

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
        user: :class:`disnake.User`
            The user to give cookies to
        amount: :class:`int`
            The amount of cookies to give
        """
        ...

Specifying the types isn't necessary, the docstring will still work:

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
        user:
            The user to give cookies to
        amount:
            The amount of cookies to give
        """
        ...

.. note ::
    You can remove ``:`` after the parameter names if you prefer the numpy format.

If you don't want to spend too many lines, just paste the description after ``:``, like so:

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
