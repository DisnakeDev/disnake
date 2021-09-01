.. currentmodule:: disnake

API Reference
===============

The following section outlines the API of disnake's command extension module.

.. _ext_commands_api_bot:

Bots
------

Bot
~~~~

.. attributetable:: disnake.ext.commands.Bot

.. autoclass:: disnake.ext.commands.Bot
    :members:
    :inherited-members:
    :exclude-members: after_invoke, before_invoke, check, check_once, command, event, group, listen

    .. automethod:: Bot.after_invoke()
        :decorator:

    .. automethod:: Bot.before_invoke()
        :decorator:

    .. automethod:: Bot.check()
        :decorator:

    .. automethod:: Bot.check_once()
        :decorator:

    .. automethod:: Bot.command(*args, **kwargs)
        :decorator:
    
    .. automethod:: Bot.event()
        :decorator:

    .. automethod:: Bot.group(*args, **kwargs)
        :decorator:

    .. automethod:: Bot.listen(name=None)
        :decorator:

AutoShardedBot
~~~~~~~~~~~~~~~~

.. attributetable:: disnake.ext.commands.AutoShardedBot

.. autoclass:: disnake.ext.commands.AutoShardedBot
    :members:

Prefix Helpers
----------------

.. autofunction:: disnake.ext.commands.when_mentioned

.. autofunction:: disnake.ext.commands.when_mentioned_or

.. _ext_commands_api_events:

Event Reference
-----------------

These events function similar to :ref:`the regular events <disnake-api-events>`, except they
are custom to the command extension module.

.. function:: disnake.ext.commands.on_command_error(ctx, error)

    An error handler that is called when an error is raised
    inside a command either through user input error, check
    failure, or an error in your own code.

    A default one is provided (:meth:`.Bot.on_command_error`).

    :param ctx: The invocation context.
    :type ctx: :class:`.Context`
    :param error: The error that was raised.
    :type error: :class:`.CommandError` derived

.. function:: disnake.ext.commands.on_command(ctx)

    An event that is called when a command is found and is about to be invoked.

    This event is called regardless of whether the command itself succeeds via
    error or completes.

    :param ctx: The invocation context.
    :type ctx: :class:`.Context`

.. function:: disnake.ext.commands.on_command_completion(ctx)

    An event that is called when a command has completed its invocation.

    This event is called only if the command succeeded, i.e. all checks have
    passed and the user input it correctly.

    :param ctx: The invocation context.
    :type ctx: :class:`.Context`

.. _ext_commands_api_command:

Commands
----------

Decorators
~~~~~~~~~~~~

.. autofunction:: disnake.ext.commands.command
    :decorator:

.. autofunction:: disnake.ext.commands.group
    :decorator:

Command
~~~~~~~~~

.. attributetable:: disnake.ext.commands.Command

.. autoclass:: disnake.ext.commands.Command
    :members:
    :special-members: __call__
    :exclude-members: after_invoke, before_invoke, error

    .. automethod:: Command.after_invoke()
        :decorator:

    .. automethod:: Command.before_invoke()
        :decorator:

    .. automethod:: Command.error()
        :decorator:

Group
~~~~~~

.. attributetable:: disnake.ext.commands.Group

.. autoclass:: disnake.ext.commands.Group
    :members:
    :inherited-members:
    :exclude-members: after_invoke, before_invoke, command, error, group

    .. automethod:: Group.after_invoke()
        :decorator:

    .. automethod:: Group.before_invoke()
        :decorator:

    .. automethod:: Group.command(*args, **kwargs)
        :decorator:

    .. automethod:: Group.error()
        :decorator:

    .. automethod:: Group.group(*args, **kwargs)
        :decorator:

GroupMixin
~~~~~~~~~~~

.. attributetable:: disnake.ext.commands.GroupMixin

.. autoclass:: disnake.ext.commands.GroupMixin
    :members:
    :exclude-members: command, group

    .. automethod:: GroupMixin.command(*args, **kwargs)
        :decorator:

    .. automethod:: GroupMixin.group(*args, **kwargs)
        :decorator:

.. _ext_commands_api_cogs:

Cogs
------

Cog
~~~~

.. attributetable:: disnake.ext.commands.Cog

.. autoclass:: disnake.ext.commands.Cog
    :members:

CogMeta
~~~~~~~~

.. attributetable:: disnake.ext.commands.CogMeta

.. autoclass:: disnake.ext.commands.CogMeta
    :members:

.. _ext_commands_help_command:

Help Commands
---------------

HelpCommand
~~~~~~~~~~~~

.. attributetable:: disnake.ext.commands.HelpCommand

.. autoclass:: disnake.ext.commands.HelpCommand
    :members:

DefaultHelpCommand
~~~~~~~~~~~~~~~~~~~

.. attributetable:: disnake.ext.commands.DefaultHelpCommand

.. autoclass:: disnake.ext.commands.DefaultHelpCommand
    :members:
    :exclude-members: send_bot_help, send_cog_help, send_group_help, send_command_help, prepare_help_command

MinimalHelpCommand
~~~~~~~~~~~~~~~~~~~

.. attributetable:: disnake.ext.commands.MinimalHelpCommand

.. autoclass:: disnake.ext.commands.MinimalHelpCommand
    :members:
    :exclude-members: send_bot_help, send_cog_help, send_group_help, send_command_help, prepare_help_command

Paginator
~~~~~~~~~~

.. attributetable:: disnake.ext.commands.Paginator

.. autoclass:: disnake.ext.commands.Paginator
    :members:

Enums
------

.. class:: BucketType
    :module: disnake.ext.commands

    Specifies a type of bucket for, e.g. a cooldown.

    .. attribute:: default

        The default bucket operates on a global basis.
    .. attribute:: user

        The user bucket operates on a per-user basis.
    .. attribute:: guild

        The guild bucket operates on a per-guild basis.
    .. attribute:: channel

        The channel bucket operates on a per-channel basis.
    .. attribute:: member

        The member bucket operates on a per-member basis.
    .. attribute:: category

        The category bucket operates on a per-category basis.
    .. attribute:: role

        The role bucket operates on a per-role basis.

        .. versionadded:: 1.3


.. _ext_commands_api_checks:

Checks
-------

.. autofunction:: disnake.ext.commands.check(predicate)
    :decorator:

.. autofunction:: disnake.ext.commands.check_any(*checks)
    :decorator:

.. autofunction:: disnake.ext.commands.has_role(item)
    :decorator:

.. autofunction:: disnake.ext.commands.has_permissions(**perms)
    :decorator:

.. autofunction:: disnake.ext.commands.has_guild_permissions(**perms)
    :decorator:

.. autofunction:: disnake.ext.commands.has_any_role(*items)
    :decorator:

.. autofunction:: disnake.ext.commands.bot_has_role(item)
    :decorator:

.. autofunction:: disnake.ext.commands.bot_has_permissions(**perms)
    :decorator:

.. autofunction:: disnake.ext.commands.bot_has_guild_permissions(**perms)
    :decorator:

.. autofunction:: disnake.ext.commands.bot_has_any_role(*items)
    :decorator:

.. autofunction:: disnake.ext.commands.cooldown(rate, per, type=disnake.ext.commands.BucketType.default)
    :decorator:

.. autofunction:: disnake.ext.commands.dynamic_cooldown(cooldown, type=BucketType.default)
    :decorator:

.. autofunction:: disnake.ext.commands.max_concurrency(number, per=disnake.ext.commands.BucketType.default, *, wait=False)
    :decorator:

.. autofunction:: disnake.ext.commands.before_invoke(coro)
    :decorator:

.. autofunction:: disnake.ext.commands.after_invoke(coro)
    :decorator:

.. autofunction:: disnake.ext.commands.guild_only(,)
    :decorator:

.. autofunction:: disnake.ext.commands.dm_only(,)
    :decorator:

.. autofunction:: disnake.ext.commands.is_owner(,)
    :decorator:

.. autofunction:: disnake.ext.commands.is_nsfw(,)
    :decorator:

.. _ext_commands_api_context:

Cooldown
---------

.. attributetable:: disnake.ext.commands.Cooldown

.. autoclass:: disnake.ext.commands.Cooldown
    :members:

Context
--------

.. attributetable:: disnake.ext.commands.Context

.. autoclass:: disnake.ext.commands.Context
    :members:
    :inherited-members:
    :exclude-members: history, typing

    .. automethod:: disnake.ext.commands.Context.history
        :async-for:

    .. automethod:: disnake.ext.commands.Context.typing
        :async-with:

.. _ext_commands_api_converters:

Converters
------------

.. autoclass:: disnake.ext.commands.Converter
    :members:

.. autoclass:: disnake.ext.commands.ObjectConverter
    :members:

.. autoclass:: disnake.ext.commands.MemberConverter
    :members:

.. autoclass:: disnake.ext.commands.UserConverter
    :members:

.. autoclass:: disnake.ext.commands.MessageConverter
    :members:

.. autoclass:: disnake.ext.commands.PartialMessageConverter
    :members:

.. autoclass:: disnake.ext.commands.GuildChannelConverter
    :members:

.. autoclass:: disnake.ext.commands.TextChannelConverter
    :members:

.. autoclass:: disnake.ext.commands.VoiceChannelConverter
    :members:

.. autoclass:: disnake.ext.commands.StoreChannelConverter
    :members:

.. autoclass:: disnake.ext.commands.StageChannelConverter
    :members:

.. autoclass:: disnake.ext.commands.CategoryChannelConverter
    :members:

.. autoclass:: disnake.ext.commands.InviteConverter
    :members:

.. autoclass:: disnake.ext.commands.GuildConverter
    :members:

.. autoclass:: disnake.ext.commands.RoleConverter
    :members:

.. autoclass:: disnake.ext.commands.GameConverter
    :members:

.. autoclass:: disnake.ext.commands.ColourConverter
    :members:

.. autoclass:: disnake.ext.commands.EmojiConverter
    :members:

.. autoclass:: disnake.ext.commands.PartialEmojiConverter
    :members:

.. autoclass:: disnake.ext.commands.ThreadConverter
    :members:

.. autoclass:: disnake.ext.commands.GuildStickerConverter
    :members:

.. autoclass:: disnake.ext.commands.clean_content
    :members:

.. autoclass:: disnake.ext.commands.Greedy()

.. autofunction:: disnake.ext.commands.run_converters

Flag Converter
~~~~~~~~~~~~~~~

.. autoclass:: disnake.ext.commands.FlagConverter
    :members:

.. autoclass:: disnake.ext.commands.Flag()
    :members:

.. autofunction:: disnake.ext.commands.flag

.. _ext_commands_api_errors:

Exceptions
-----------

.. autoexception:: disnake.ext.commands.CommandError
    :members:

.. autoexception:: disnake.ext.commands.ConversionError
    :members:

.. autoexception:: disnake.ext.commands.MissingRequiredArgument
    :members:

.. autoexception:: disnake.ext.commands.ArgumentParsingError
    :members:

.. autoexception:: disnake.ext.commands.UnexpectedQuoteError
    :members:

.. autoexception:: disnake.ext.commands.InvalidEndOfQuotedStringError
    :members:

.. autoexception:: disnake.ext.commands.ExpectedClosingQuoteError
    :members:

.. autoexception:: disnake.ext.commands.BadArgument
    :members:

.. autoexception:: disnake.ext.commands.BadUnionArgument
    :members:

.. autoexception:: disnake.ext.commands.BadLiteralArgument
    :members:

.. autoexception:: disnake.ext.commands.PrivateMessageOnly
    :members:

.. autoexception:: disnake.ext.commands.NoPrivateMessage
    :members:

.. autoexception:: disnake.ext.commands.CheckFailure
    :members:

.. autoexception:: disnake.ext.commands.CheckAnyFailure
    :members:

.. autoexception:: disnake.ext.commands.CommandNotFound
    :members:

.. autoexception:: disnake.ext.commands.DisabledCommand
    :members:

.. autoexception:: disnake.ext.commands.CommandInvokeError
    :members:

.. autoexception:: disnake.ext.commands.TooManyArguments
    :members:

.. autoexception:: disnake.ext.commands.UserInputError
    :members:

.. autoexception:: disnake.ext.commands.CommandOnCooldown
    :members:

.. autoexception:: disnake.ext.commands.MaxConcurrencyReached
    :members:

.. autoexception:: disnake.ext.commands.NotOwner
    :members:

.. autoexception:: disnake.ext.commands.MessageNotFound
    :members:

.. autoexception:: disnake.ext.commands.MemberNotFound
    :members:

.. autoexception:: disnake.ext.commands.GuildNotFound
    :members:

.. autoexception:: disnake.ext.commands.UserNotFound
    :members:

.. autoexception:: disnake.ext.commands.ChannelNotFound
    :members:

.. autoexception:: disnake.ext.commands.ChannelNotReadable
    :members:

.. autoexception:: disnake.ext.commands.ThreadNotFound
    :members:

.. autoexception:: disnake.ext.commands.BadColourArgument
    :members:

.. autoexception:: disnake.ext.commands.RoleNotFound
    :members:

.. autoexception:: disnake.ext.commands.BadInviteArgument
    :members:

.. autoexception:: disnake.ext.commands.EmojiNotFound
    :members:

.. autoexception:: disnake.ext.commands.PartialEmojiConversionFailure
    :members:

.. autoexception:: disnake.ext.commands.GuildStickerNotFound
    :members:

.. autoexception:: disnake.ext.commands.BadBoolArgument
    :members:

.. autoexception:: disnake.ext.commands.MissingPermissions
    :members:

.. autoexception:: disnake.ext.commands.BotMissingPermissions
    :members:

.. autoexception:: disnake.ext.commands.MissingRole
    :members:

.. autoexception:: disnake.ext.commands.BotMissingRole
    :members:

.. autoexception:: disnake.ext.commands.MissingAnyRole
    :members:

.. autoexception:: disnake.ext.commands.BotMissingAnyRole
    :members:

.. autoexception:: disnake.ext.commands.NSFWChannelRequired
    :members:

.. autoexception:: disnake.ext.commands.FlagError
    :members:

.. autoexception:: disnake.ext.commands.BadFlagArgument
    :members:

.. autoexception:: disnake.ext.commands.MissingFlagArgument
    :members:

.. autoexception:: disnake.ext.commands.TooManyFlags
    :members:

.. autoexception:: disnake.ext.commands.MissingRequiredFlag
    :members:

.. autoexception:: disnake.ext.commands.ExtensionError
    :members:

.. autoexception:: disnake.ext.commands.ExtensionAlreadyLoaded
    :members:

.. autoexception:: disnake.ext.commands.ExtensionNotLoaded
    :members:

.. autoexception:: disnake.ext.commands.NoEntryPointError
    :members:

.. autoexception:: disnake.ext.commands.ExtensionFailed
    :members:

.. autoexception:: disnake.ext.commands.ExtensionNotFound
    :members:

.. autoexception:: disnake.ext.commands.CommandRegistrationError
    :members:


Exception Hierarchy
~~~~~~~~~~~~~~~~~~~~~

.. exception_hierarchy::

    - :exc:`~.DiscordException`
        - :exc:`~.commands.CommandError`
            - :exc:`~.commands.ConversionError`
            - :exc:`~.commands.UserInputError`
                - :exc:`~.commands.MissingRequiredArgument`
                - :exc:`~.commands.TooManyArguments`
                - :exc:`~.commands.BadArgument`
                    - :exc:`~.commands.MessageNotFound`
                    - :exc:`~.commands.MemberNotFound`
                    - :exc:`~.commands.GuildNotFound`
                    - :exc:`~.commands.UserNotFound`
                    - :exc:`~.commands.ChannelNotFound`
                    - :exc:`~.commands.ChannelNotReadable`
                    - :exc:`~.commands.BadColourArgument`
                    - :exc:`~.commands.RoleNotFound`
                    - :exc:`~.commands.BadInviteArgument`
                    - :exc:`~.commands.EmojiNotFound`
                    - :exc:`~.commands.GuildStickerNotFound`
                    - :exc:`~.commands.PartialEmojiConversionFailure`
                    - :exc:`~.commands.BadBoolArgument`
                    - :exc:`~.commands.ThreadNotFound`
                    - :exc:`~.commands.FlagError`
                        - :exc:`~.commands.BadFlagArgument`
                        - :exc:`~.commands.MissingFlagArgument`
                        - :exc:`~.commands.TooManyFlags`
                        - :exc:`~.commands.MissingRequiredFlag`
                - :exc:`~.commands.BadUnionArgument`
                - :exc:`~.commands.BadLiteralArgument`
                - :exc:`~.commands.ArgumentParsingError`
                    - :exc:`~.commands.UnexpectedQuoteError`
                    - :exc:`~.commands.InvalidEndOfQuotedStringError`
                    - :exc:`~.commands.ExpectedClosingQuoteError`
            - :exc:`~.commands.CommandNotFound`
            - :exc:`~.commands.CheckFailure`
                - :exc:`~.commands.CheckAnyFailure`
                - :exc:`~.commands.PrivateMessageOnly`
                - :exc:`~.commands.NoPrivateMessage`
                - :exc:`~.commands.NotOwner`
                - :exc:`~.commands.MissingPermissions`
                - :exc:`~.commands.BotMissingPermissions`
                - :exc:`~.commands.MissingRole`
                - :exc:`~.commands.BotMissingRole`
                - :exc:`~.commands.MissingAnyRole`
                - :exc:`~.commands.BotMissingAnyRole`
                - :exc:`~.commands.NSFWChannelRequired`
            - :exc:`~.commands.DisabledCommand`
            - :exc:`~.commands.CommandInvokeError`
            - :exc:`~.commands.CommandOnCooldown`
            - :exc:`~.commands.MaxConcurrencyReached`
        - :exc:`~.commands.ExtensionError`
            - :exc:`~.commands.ExtensionAlreadyLoaded`
            - :exc:`~.commands.ExtensionNotLoaded`
            - :exc:`~.commands.NoEntryPointError`
            - :exc:`~.commands.ExtensionFailed`
            - :exc:`~.commands.ExtensionNotFound`
    - :exc:`~.ClientException`
        - :exc:`~.commands.CommandRegistrationError`
