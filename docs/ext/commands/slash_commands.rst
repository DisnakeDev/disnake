.. SPDX-License-Identifier: MIT

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

By default, the registration is global. This means that your slash commands will be visible everywhere, including bot DMs,
though you can adjust this by setting specific :ref:`contexts <app_command_contexts>`.
You can also change the registration to be local, so your slash commands will only be visible in several guilds.

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

In order to configure specific properties about command sync, there's a configuration
class which may be passed to the Bot, :class:`~.ext.commands.CommandSyncFlags`.

Setting :attr:`CommandSyncFlags.sync_commands_debug <.ext.commands.CommandSyncFlags.sync_commands_debug>` to ``True``, will print debug messages related to the
app command registration to the console (or logger if enabled).

This is useful if you want to figure out some registration details:

.. code-block:: python3

    from disnake.ext import commands

    command_sync_flags = commands.CommandSyncFlags.default()
    command_sync_flags.sync_commands_debug = True

    bot = commands.Bot(
        command_prefix='!',
        test_guilds=[123456789], # Optional
        command_sync_flags=command_sync_flags,
    )

If you want to disable the automatic registration, set :attr:`CommandSyncFlags.sync_commands <.ext.commands.CommandSyncFlags.sync_commands>`
to ``False``, or use :meth:`CommandSyncFlags.none() <.ext.commands.CommandSyncFlags.none>`

.. code-block:: python3

    from disnake.ext import commands

    command_sync_flags = commands.CommandSyncFlags.none()
    command_sync_flags.sync_commands = False

    bot = commands.Bot(
        command_prefix='!',
        command_sync_flags=command_sync_flags,
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
- :class:`disnake.abc.GuildChannel`\*
- :class:`disnake.User` or :class:`disnake.Member`\*\*
- :class:`disnake.Role`\*\*
- :class:`disnake.Attachment`
- :class:`disnake.abc.Snowflake`\*\*\*

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
  \* All channel subclasses and unions (e.g. ``Union[TextChannel, StageChannel]``) are also supported.
  See :attr:`ParamInfo.channel_types <ext.commands.ParamInfo>` for more fine-grained control.

  \*\* Some combinations of types are also allowed, including:
    - ``Union[User, Member]`` (results in :class:`OptionType.user`)
    - ``Union[Member, Role]`` (results in :class:`OptionType.mentionable`)
    - ``Union[User, Role]`` (results in :class:`OptionType.mentionable`)
    - ``Union[User, Member, Role]`` (results in :class:`OptionType.mentionable`)

  Note that a :class:`~disnake.User` annotation can also result in a :class:`~disnake.Member` being received.

  \*\*\* Corresponds to any mentionable type, currently equivalent to ``Union[User, Member, Role]``.


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


Instead of using :func:`~ext.commands.Param`, you can also use a :class:`~ext.commands.Range` annotation.
The range bounds are both inclusive; using ``...`` as a bound indicates that this end of the range is unbounded.
The type of the option is specified by the first type argument, which can be either :class:`int` or :class:`float`.

.. code-block:: python3

    @bot.slash_command()
    async def ranges(
        inter: disnake.ApplicationCommandInteraction,
        a: commands.Range[int, 0, 10],       # 0 - 10 int
        b: commands.Range[float, 0, 10.0],     # 0 - 10 float
        c: commands.Range[int, 1, ...],      # positive int
    ):
        ...

.. _string_lengths:

String Lengths
++++++++++++++

:class:`str` parameters support minimum and maximum allowed lengths
using the ``min_length`` and ``max_length`` parameters on :func:`~ext.commands.Param`.
For instance, you could restrict an option to only accept a single character:

.. code-block:: python3

    @bot.slash_command()
    async def charinfo(
        inter: disnake.ApplicationCommandInteraction,
        character: str = commands.Param(max_length=1),
    ):
        ...

Or restrict a tag command to limit tag names to 20 characters:

.. code-block:: python3

    @bot.slash_command()
    async def tags(
        inter: disnake.ApplicationCommandInteraction,
        tag: str = commands.Param(max_length=20)
    ):
        ...

Instead of using :func:`~ext.commands.Param`, you can also use a :class:`~ext.commands.String` annotation.
The length bounds are both inclusive; using ``...`` as a bound indicates that this end of the string length is unbounded.
The first type argument should always be :class:`str`.

.. code-block:: python3

    @bot.slash_command()
    async def strings(
        inter: disnake.ApplicationCommandInteraction,
        a: commands.String[str, 0, 10],       # a str no longer than 10 characters.
        b: commands.String[str, 10, 100],     # a str that's at least 10 characters but not longer than 100.
        c: commands.String[str, 50, ...],     # a str that's at least 50 characters.
    ):
        ...

.. note::

    There is a max length of 6000 characters, which is enforced by Discord.

.. _docstrings:

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
    async def languages(inter: disnake.ApplicationCommandInteraction, language: str):
        pass


    @languages.autocomplete("language")
    async def language_autocomp(inter: disnake.ApplicationCommandInteraction, string: str):
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

We have them, look at `this example <https://github.com/DisnakeDev/disnake/blob/master/examples/interactions/injections.py>`__ for more information ✨


.. _localizations:

Localizations
-------------

The names and descriptions of commands and options, as well as the names of choices
(for use with fixed choices or autocompletion), support localization for a fixed set of locales.

For currently supported locales, see :class:`Locale`.

.. note::
    You can supply your own custom localization provider by implementing :class:`.LocalizationProtocol`
    and using the client's/bot's ``localization_provider`` parameter to  :class:`~ext.commands.Bot`.
    The ``.json`` handling mentioned in this section, as well as the :ref:`localizations_strict` section below only
    apply to the default implementation, :class:`.LocalizationStore`.

The preferred way of adding localizations is to use ``<locale>.json`` files,
containing mappings from user-defined keys to localized/translated strings,
and referencing these keys in the commands' :ref:`docstrings <docstrings>`.
As an example, consider this command:

.. code-block:: python3

    @bot.slash_command()
    async def add_5(inter: disnake.ApplicationCommandInteraction, num: int):
        """
        Adds 5 to a number. {{ADD_NUM}}

        Parameters
        ----------
        num: Some number {{ COOL_NUMBER }}
        """
        await inter.response.send_message(f"{num} + 5 = {num + 5}")

The keys ``{{XYZ}}`` are automatically extracted from the docstrings,
and used for looking up names ``XYZ_NAME`` and descriptions ``XYZ_DESCRIPTION``.
Note that whitespace is ignored, and the positioning inside the line doesn't matter.

For instance, to add German localizations, create a ``locale/de.json`` file;
the directory name/path can be changed arbitrarily, ``locale`` is just the one used here:

.. code-block:: json

    {
        "ADD_NUM_NAME": "addiere_5",
        "ADD_NUM_DESCRIPTION": "Addiere 5 zu einer anderen Zahl.",
        "COOL_NUMBER_NAME": "zahl",
        "COOL_NUMBER_DESCRIPTION": "Eine Zahl"
    }

To load a directory or file containing localizations, use :func:`bot.i18n.load(path) <disnake.LocalizationStore.load>`:

.. code-block:: python3

    ...
    bot.i18n.load("locale/")  # loads all files in the "locale/" directory
    bot.run(...)

.. note::
    If :attr:`Bot.reload <ext.commands.Bot.reload>` is ``True``, all currently loaded localization files
    are reloaded when an extension gets automatically reloaded.


.. _localizations_strict:

Strict Localization
+++++++++++++++++++

By default, missing keys that couldn't be found are silently ignored.
To instead raise an exception when a key is missing, pass the ``strict_localization=True`` parameter to the client/bot constructor
(see the docs for the ``strict_localization`` parameter to :class:`~.ext.commands.Bot`).


Customization
+++++++++++++

If you want more customization or low-level control over localizations, you can specify arbitrary keys for the commands/options directly.
:class:`.Localized` takes the non-localized string (optional depending on target type) to keep the ability of e.g.
overwriting ``name`` in the command decorator, and either a ``key`` or ``data`` parameter.

This would create the same command as the code above, though you're free to change the keys like ``ADD_NUM_DESCRIPTION`` however you want:

.. code-block:: python3

    @bot.slash_command(name=Localized("add_5", key="ADD_NUM_NAME"), description=Localized(key="ADD_NUM_DESCRIPTION"))
    async def _add_5_slash(
        inter: disnake.ApplicationCommandInteraction,
        num: int = commands.Param(
            name=Localized(key="COOL_NUMBER_NAME"),
            description=Localized(key="COOL_NUMBER_DESCRIPTION")
        ),
    ):
        """
        Adds 5 to a number.

        Parameters
        ----------
        num: Some number
        """
        await inter.response.send_message(f"{num} + 5 = {num + 5}")

While not recommended, it is also possible to avoid using ``.json`` files at all, and instead specify localizations directly in the code:

.. code-block:: python3

    @bot.slash_command(
        name=Localized(data={Locale.de: "addiere_5"}),
        description=Localized(data={Locale.de: "Addiere 5 zu einer anderen Zahl."}),
    )
    async def add_5(
        inter: disnake.ApplicationCommandInteraction,
        num: int = commands.Param(
            name=Localized(data={Locale.de: "zahl"}),
            description=Localized(data={Locale.de: "Eine Zahl"}),
        ),
    ):
        ...


Choices/Autocomplete
++++++++++++++++++++

:ref:`Option choices <option_choices>` and :ref:`autocomplete items <autocompleters>` can also be localized, through the use of :class:`OptionChoice`:

.. code-block:: python3

    @bot.slash_command()
    async def example(
        inter: disnake.ApplicationCommandInteraction,
        animal: str = commands.Param(choices=[
            # alternatively:
            # OptionChoice(Localized("Cat", key="OPTION_CAT"), "Cat")
            Localized("Cat", key="OPTION_CAT"),
            Localized("Dolphin", key="OPTION_DOLPHIN"),
        ]),
        language: str = commands.Param(autocomplete=autocomp_langs),
    ):
        ...

    @example.autocomplete("language")
    async def language_autocomp(inter: disnake.ApplicationCommandInteraction, user_input: str):
        languages = ("english", "german", "spanish", "japanese")
        return [
            # alternatively:
            # `OptionChoice(Localized(lang, key=f"AUTOCOMP_{lang.upper()}"), lang)`
            Localized(lang, key=f"AUTOCOMP_{lang.upper()}")
            for lang in languages
            if user_input.lower() in lang
        ]

Yet again, with a file like ``locale/de.json`` containing localizations like this:

.. code-block:: json

    {
        "OPTION_CAT": "Katze",
        "OPTION_DOLPHIN": "Delfin",
        "AUTOCOMP_ENGLISH": "Englisch",
        "AUTOCOMP_GERMAN": "Deutsch",
        "AUTOCOMP_SPANISH": "Spanisch",
        "AUTOCOMP_JAPANESE": "Japanisch"
    }


.. _app_command_contexts:

Installation/Interaction Contexts
---------------------------------

The :attr:`~ApplicationCommand.install_types` and :attr:`~ApplicationCommand.contexts` command
attributes allow you to control how and where your command can be run.

.. note::
    These fields cannot be configured for a slash subcommand or
    subcommand group, only in top-level slash commands and user/message commands.

Install Types
+++++++++++++

The :attr:`~ApplicationCommand.install_types` field determines whether your command can be used
when the bot is installed to a guild, a user, or both.

Bots installed to a **guild** are visible to *all members*, which used to be the only entry point for users
to run commands. Alternatively, bots can now also support being installed to a **user**, which makes
the commands available everywhere to the *authorizing user* only.

For instance, to make a command only available in a user-installed context, you can
use the :func:`~.ext.commands.install_types` decorator:

.. code-block:: python3

    @bot.slash_command()
    @commands.install_types(user=True)
    async def command(inter: disnake.ApplicationCommandInteraction):
        ...

Alternatively, you may pass e.g. ``install_types=disnake.ApplicationInstallTypes(user=True)``
as an argument directly to the command decorator. To allow all (guild + user) installation types,
a :meth:`ApplicationInstallTypes.all` shorthand is also available.

By default, commands are set to only be usable in guild-installed contexts.

.. note::
    To enable installing the bot in user contexts (or disallow guild contexts), you will need to
    adjust the settings in the **Developer Portal** on the application's **"Installation"** page.

Contexts
++++++++

While ``install_types`` determines where the bot must be *installed* to run a command,
:attr:`~ApplicationCommand.contexts` dictates where *in Discord* a command can be used.

Possible surfaces are **guilds**, **DMs with the bot**, and **DMs (and group DMs) between other users**,
by setting :attr:`~InteractionContextTypes.guild`, :attr:`~InteractionContextTypes.bot_dm`,
or :attr:`~InteractionContextTypes.private_channel` respectively to ``True``.
The :attr:`~InteractionContextTypes.private_channel` context is only meaningful for user-installed
commands.

Similarly to ``install_types``, this can be accomplished using the :func:`~.ext.commands.contexts`
decorator, to e.g. disallow a command in guilds:

.. code-block:: python3

    @bot.slash_command()
    @commands.contexts(bot_dm=True, private_channel=True)
    async def command(inter: disnake.ApplicationCommandInteraction):
        ...

In the same way, you can use the ``contexts=`` parameter and :class:`InteractionContextTypes` in the command decorator directly.

The default context for commands is :attr:`~InteractionContextTypes.guild` + :attr:`~InteractionContextTypes.bot_dm`.

This attribute supersedes the old ``dm_permission`` field, which can now be considered
equivalent to the :attr:`~InteractionContextTypes.bot_dm` flag.
Therefore, to prevent a command from being run in DMs, use ``InteractionContextTypes(guild=True)``.

Interaction Data
++++++++++++++++

For a given :class:`ApplicationCommandInteraction`, you can determine the context where the interaction
was triggered from using the :attr:`~ApplicationCommandInteraction.context` field.

To see how the command was installed, use the :attr:`~ApplicationCommandInteraction.authorizing_integration_owners`
field, which includes installation details relevant to that specific interaction.


.. _app_command_permissions:

Default Member Permissions
--------------------------

Using the :attr:`~ApplicationCommand.default_member_permissions` command attribute,
you can restrict by whom a command can be run in a guild by default.

These commands will not be enabled/visible for members who do not have all the required guild permissions.
In this example both the ``manage_guild`` and the ``moderate_members`` permissions would be required:

.. code-block:: python3

    @bot.slash_command()
    @commands.default_member_permissions(manage_guild=True, moderate_members=True)
    async def command(inter: disnake.ApplicationCommandInteraction):
        ...

Or use the ``default_member_permissions`` parameter in the application command decorator:

.. code-block:: python3

    @bot.slash_command(default_member_permissions=disnake.Permissions(manage_guild=True, moderate_members=True))
    async def command(inter: disnake.ApplicationCommandInteraction):
        ...

This can be overridden by moderators on a per-guild basis; ``default_member_permissions`` may be
ignored entirely once a permission override — application-wide or for this command in particular — is configured
in the guild settings, and will be restored if the permissions are re-synced in the settings.

Like the previous fields, this cannot be configured for a slash subcommand or
subcommand group, only in top-level slash commands and user/message commands.
