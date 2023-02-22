.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake.ext.commands

API Reference
===============

The following section outlines the API of disnake's command extension module.

.. _ext_commands_api_bot:

Bots
------

Bot
~~~~

.. attributetable:: Bot

.. autoclass:: Bot
    :members:
    :inherited-members:
    :exclude-members: after_invoke, before_invoke, check, check_once, command, event, group, listen, slash_command, user_command, message_command, after_slash_command_invoke, after_user_command_invoke, after_message_command_invoke, before_slash_command_invoke, before_user_command_invoke, before_message_command_invoke

    .. automethod:: Bot.after_invoke()
        :decorator:

    .. automethod:: Bot.after_slash_command_invoke()
        :decorator:

    .. automethod:: Bot.after_user_command_invoke()
        :decorator:

    .. automethod:: Bot.after_message_command_invoke()
        :decorator:

    .. automethod:: Bot.before_invoke()
        :decorator:

    .. automethod:: Bot.before_slash_command_invoke()
        :decorator:

    .. automethod:: Bot.before_user_command_invoke()
        :decorator:

    .. automethod:: Bot.before_message_command_invoke()
        :decorator:

    .. automethod:: Bot.check()
        :decorator:

    .. automethod:: Bot.check_once()
        :decorator:

    .. automethod:: Bot.command(*args, **kwargs)
        :decorator:

    .. automethod:: Bot.slash_command(*args, **kwargs)
        :decorator:

    .. automethod:: Bot.user_command(*args, **kwargs)
        :decorator:

    .. automethod:: Bot.message_command(*args, **kwargs)
        :decorator:

    .. automethod:: Bot.event()
        :decorator:

    .. automethod:: Bot.group(*args, **kwargs)
        :decorator:

    .. automethod:: Bot.listen(name=None)
        :decorator:

AutoShardedBot
~~~~~~~~~~~~~~~~

.. attributetable:: AutoShardedBot

.. autoclass:: AutoShardedBot
    :members:

InteractionBot
~~~~~~~~~~~~~~~~

.. attributetable:: InteractionBot

.. autoclass:: InteractionBot
    :members:
    :inherited-members:
    :exclude-members: after_slash_command_invoke, after_user_command_invoke, after_message_command_invoke, before_slash_command_invoke, before_user_command_invoke, before_message_command_invoke, application_command_check, slash_command_check, user_command_check, message_command_check, slash_command_check_once, user_command_check_once, message_command_check_once, event, listen, slash_command, user_command, message_command

    .. automethod:: InteractionBot.after_slash_command_invoke()
        :decorator:

    .. automethod:: InteractionBot.after_user_command_invoke()
        :decorator:

    .. automethod:: InteractionBot.after_message_command_invoke()
        :decorator:

    .. automethod:: InteractionBot.before_slash_command_invoke()
        :decorator:

    .. automethod:: InteractionBot.before_user_command_invoke()
        :decorator:

    .. automethod:: InteractionBot.before_message_command_invoke()
        :decorator:

    .. automethod:: InteractionBot.application_command_check()
        :decorator:

    .. automethod:: InteractionBot.slash_command_check()
        :decorator:

    .. automethod:: InteractionBot.user_command_check()
        :decorator:

    .. automethod:: InteractionBot.message_command_check()
        :decorator:

    .. automethod:: InteractionBot.slash_command_check_once()
        :decorator:

    .. automethod:: InteractionBot.user_command_check_once()
        :decorator:

    .. automethod:: InteractionBot.message_command_check_once()
        :decorator:

    .. automethod:: InteractionBot.slash_command(*args, **kwargs)
        :decorator:

    .. automethod:: InteractionBot.user_command(*args, **kwargs)
        :decorator:

    .. automethod:: InteractionBot.message_command(*args, **kwargs)
        :decorator:

    .. automethod:: InteractionBot.event()
        :decorator:

    .. automethod:: InteractionBot.listen(name=None)
        :decorator:

AutoShardedInteractionBot
~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: AutoShardedInteractionBot

.. autoclass:: AutoShardedInteractionBot
    :members:

Command Sync
-------------

CommandSyncFlags
~~~~~~~~~~~~~~~~~

.. attributetable:: CommandSyncFlags

.. autoclass:: CommandSyncFlags()
    :members:


Prefix Helpers
----------------

.. autofunction:: when_mentioned

.. autofunction:: when_mentioned_or

.. _ext_commands_api_events:

Event Reference
-----------------

These events function similar to :ref:`the regular events <discord-api-events>`, except they
are custom to the command extension module.

.. function:: on_command_error(ctx, error)

    An error handler that is called when an error is raised
    inside a command either through user input error, check
    failure, or an error in your own code.

    A default one is provided (:meth:`.Bot.on_command_error`).

    :param ctx: The invocation context.
    :type ctx: :class:`.Context`
    :param error: The error that was raised.
    :type error: :class:`.CommandError` derived

.. function:: on_slash_command_error(inter, error)

    An error handler that is called when an error is raised
    inside a slash command either through user input error, check
    failure, or an error in your own code.

    A default one is provided (:meth:`.Bot.on_slash_command_error`).

    :param inter: The interaction that invoked this slash command.
    :type inter: :class:`.ApplicationCommandInteraction`
    :param error: The error that was raised.
    :type error: :class:`.CommandError` derived

.. function:: on_user_command_error(inter, error)

    An error handler that is called when an error is raised
    inside a user command either through check
    failure, or an error in your own code.

    A default one is provided (:meth:`.Bot.on_user_command_error`).

    :param inter: The interaction that invoked this user command.
    :type inter: :class:`.ApplicationCommandInteraction`
    :param error: The error that was raised.
    :type error: :class:`.CommandError` derived

.. function:: on_message_command_error(inter, error)

    An error handler that is called when an error is raised
    inside a message command either through check
    failure, or an error in your own code.

    A default one is provided (:meth:`.Bot.on_message_command_error`).

    :param inter: The interaction that invoked this message command.
    :type inter: :class:`.ApplicationCommandInteraction`
    :param error: The error that was raised.
    :type error: :class:`.CommandError` derived

.. function:: on_command(ctx)

    An event that is called when a command is found and is about to be invoked.

    This event is called regardless of whether the command itself succeeds via
    error or completes.

    :param ctx: The invocation context.
    :type ctx: :class:`.Context`

.. function:: on_slash_command(inter)

    An event that is called when a slash command is found and is about to be invoked.

    This event is called regardless of whether the slash command itself succeeds via
    error or completes.

    :param inter: The interaction that invoked this slash command.
    :type inter: :class:`.ApplicationCommandInteraction`

.. function:: on_user_command(inter)

    An event that is called when a user command is found and is about to be invoked.

    This event is called regardless of whether the user command itself succeeds via
    error or completes.

    :param inter: The interaction that invoked this user command.
    :type inter: :class:`.ApplicationCommandInteraction`

.. function:: on_message_command(inter)

    An event that is called when a message command is found and is about to be invoked.

    This event is called regardless of whether the message command itself succeeds via
    error or completes.

    :param inter: The interaction that invoked this message command.
    :type inter: :class:`.ApplicationCommandInteraction`

.. function:: on_command_completion(ctx)

    An event that is called when a command has completed its invocation.

    This event is called only if the command succeeded, i.e. all checks have
    passed and the user input it correctly.

    :param ctx: The invocation context.
    :type ctx: :class:`.Context`

.. function:: on_slash_command_completion(inter)

    An event that is called when a slash command has completed its invocation.

    This event is called only if the slash command succeeded, i.e. all checks have
    passed and command handler ran successfully.

    :param inter: The interaction that invoked this slash command.
    :type inter: :class:`.ApplicationCommandInteraction`

.. function:: on_user_command_completion(inter)

    An event that is called when a user command has completed its invocation.

    This event is called only if the user command succeeded, i.e. all checks have
    passed and command handler ran successfully.

    :param inter: The interaction that invoked this user command.
    :type inter: :class:`.ApplicationCommandInteraction`

.. function:: on_message_command_completion(inter)

    An event that is called when a message command has completed its invocation.

    This event is called only if the message command succeeded, i.e. all checks have
    passed and command handler ran successfully.

    :param inter: The interaction that invoked this message command.
    :type inter: :class:`.ApplicationCommandInteraction`

.. _ext_commands_api_command:

Commands
----------

Decorators
~~~~~~~~~~~~

.. autofunction:: command
    :decorator:

.. autofunction:: slash_command
    :decorator:

.. autofunction:: user_command
    :decorator:

.. autofunction:: message_command
    :decorator:

.. autofunction:: group
    :decorator:

Helper Functions
~~~~~~~~~~~~~~~~

.. autofunction:: Param

.. autofunction:: option_enum

.. autofunction:: converter_method
    :decorator:

Application Command
~~~~~~~~~~~~~~~~~~~

.. attributetable:: InvokableApplicationCommand

.. autoclass:: InvokableApplicationCommand
    :members:
    :exclude-members: before_invoke, after_invoke, error

    .. automethod:: InvokableApplicationCommand.before_invoke()
        :decorator:

    .. automethod:: InvokableApplicationCommand.after_invoke()
        :decorator:

    .. automethod:: InvokableApplicationCommand.error()
        :decorator:

Slash Command
~~~~~~~~~~~~~

.. attributetable:: InvokableSlashCommand

.. autoclass:: InvokableSlashCommand
    :members:
    :special-members: __call__
    :exclude-members: sub_command, sub_command_group, after_invoke, before_invoke, error

    .. automethod:: InvokableSlashCommand.sub_command(*args, **kwargs)
        :decorator:

    .. automethod:: InvokableSlashCommand.sub_command_group(*args, **kwargs)
        :decorator:

    .. automethod:: InvokableSlashCommand.after_invoke()
        :decorator:

    .. automethod:: InvokableSlashCommand.before_invoke()
        :decorator:

    .. automethod:: InvokableSlashCommand.error()
        :decorator:

Slash Subcommand
~~~~~~~~~~~~~~~~

.. attributetable:: SubCommand

.. autoclass:: SubCommand
    :members:
    :exclude-members: after_invoke, before_invoke, error

    .. automethod:: SubCommand.after_invoke()
        :decorator:

    .. automethod:: SubCommand.before_invoke()
        :decorator:

    .. automethod:: SubCommand.error()
        :decorator:

Slash Subcommand Group
~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: SubCommandGroup

.. autoclass:: SubCommandGroup
    :members:
    :exclude-members: sub_command, after_invoke, before_invoke, error

    .. automethod:: SubCommandGroup.sub_command(*args, **kwargs)
        :decorator:

    .. automethod:: SubCommandGroup.after_invoke()
        :decorator:

    .. automethod:: SubCommandGroup.before_invoke()
        :decorator:

    .. automethod:: SubCommandGroup.error()
        :decorator:

ParamInfo
~~~~~~~~~

.. attributetable:: ParamInfo

.. autoclass:: ParamInfo

Injections
~~~~~~~~~~

.. attributetable:: Injection

.. autoclass:: Injection
    :members:
    :special-members: __call__
    :exclude-members: autocomplete

    .. automethod:: Injection.autocomplete
        :decorator:

.. autofunction:: inject

.. autofunction:: register_injection
    :decorator:

.. autofunction:: injection
    :decorator:

User Command
~~~~~~~~~~~~

.. attributetable:: InvokableUserCommand

.. autoclass:: InvokableUserCommand
    :members:
    :special-members: __call__
    :exclude-members: after_invoke, before_invoke, error

    .. automethod:: InvokableUserCommand.after_invoke()
        :decorator:

    .. automethod:: InvokableUserCommand.before_invoke()
        :decorator:

    .. automethod:: InvokableUserCommand.error()
        :decorator:

Message Command
~~~~~~~~~~~~~~~

.. attributetable:: InvokableMessageCommand

.. autoclass:: InvokableMessageCommand
    :members:
    :special-members: __call__
    :exclude-members: after_invoke, before_invoke, error

    .. automethod:: InvokableMessageCommand.after_invoke()
        :decorator:

    .. automethod:: InvokableMessageCommand.before_invoke()
        :decorator:

    .. automethod:: InvokableMessageCommand.error()
        :decorator:

Command
~~~~~~~~~

.. attributetable:: Command

.. autoclass:: Command
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

.. attributetable:: Group

.. autoclass:: Group
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

.. attributetable:: GroupMixin

.. autoclass:: GroupMixin
    :members:
    :exclude-members: command, group

    .. automethod:: GroupMixin.command(*args, **kwargs)
        :decorator:

    .. automethod:: GroupMixin.group(*args, **kwargs)
        :decorator:

LargeInt
~~~~~~~~

.. autoclass:: LargeInt

    This is a class which inherits from :class:`int` to allow large numbers in slash commands, meant to be used only for annotations.

Range
~~~~~

.. autoclass:: Range

String
~~~~~~

.. autoclass:: String


.. _ext_commands_api_cogs:

Cogs
------

Cog
~~~~

.. attributetable:: Cog

.. autoclass:: Cog
    :members:

CogMeta
~~~~~~~~

.. attributetable:: CogMeta

.. autoclass:: CogMeta
    :members:

.. _ext_commands_help_command:

Help Commands
---------------

HelpCommand
~~~~~~~~~~~~

.. attributetable:: HelpCommand

.. autoclass:: HelpCommand
    :members:

DefaultHelpCommand
~~~~~~~~~~~~~~~~~~~

.. attributetable:: DefaultHelpCommand

.. autoclass:: DefaultHelpCommand
    :members:
    :exclude-members: send_bot_help, send_cog_help, send_group_help, send_command_help, prepare_help_command

MinimalHelpCommand
~~~~~~~~~~~~~~~~~~~

.. attributetable:: MinimalHelpCommand

.. autoclass:: MinimalHelpCommand
    :members:
    :exclude-members: send_bot_help, send_cog_help, send_group_help, send_command_help, prepare_help_command

Paginator
~~~~~~~~~~

.. attributetable:: Paginator

.. autoclass:: Paginator
    :members:

Enums
------

.. class:: BucketType

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

.. autofunction:: check(predicate)
    :decorator:

.. autofunction:: check_any(*checks)
    :decorator:

.. autofunction:: has_role(item)
    :decorator:

.. autofunction:: has_permissions(**perms)
    :decorator:

.. autofunction:: has_guild_permissions(**perms)
    :decorator:

.. autofunction:: has_any_role(*items)
    :decorator:

.. autofunction:: bot_has_role(item)
    :decorator:

.. autofunction:: bot_has_permissions(**perms)
    :decorator:

.. autofunction:: bot_has_guild_permissions(**perms)
    :decorator:

.. autofunction:: bot_has_any_role(*items)
    :decorator:

.. autofunction:: cooldown(rate, per, type=BucketType.default)
    :decorator:

.. autofunction:: dynamic_cooldown(cooldown, type=BucketType.default)
    :decorator:

.. autofunction:: max_concurrency(number, per=BucketType.default, *, wait=False)
    :decorator:

.. autofunction:: before_invoke(coro)
    :decorator:

.. autofunction:: after_invoke(coro)
    :decorator:

.. autofunction:: guild_only(,)
    :decorator:

.. autofunction:: dm_only(,)
    :decorator:

.. autofunction:: is_owner(,)
    :decorator:

.. autofunction:: is_nsfw(,)
    :decorator:

.. autofunction:: default_member_permissions
    :decorator:

.. _ext_commands_api_context:

Cooldown
---------

.. attributetable:: Cooldown

.. autoclass:: Cooldown
    :members:

Context
--------

.. attributetable:: Context

.. autoclass:: Context
    :members:
    :inherited-members:
    :exclude-members: history, typing

    .. automethod:: Context.history
        :async-for:

    .. automethod:: Context.typing
        :async-with:

.. _ext_commands_api_converters:

Converters
------------

.. autoclass:: Converter
    :members:

.. autoclass:: ObjectConverter
    :members:

.. autoclass:: MemberConverter
    :members:

.. autoclass:: UserConverter
    :members:

.. autoclass:: MessageConverter
    :members:

.. autoclass:: PartialMessageConverter
    :members:

.. autoclass:: GuildChannelConverter
    :members:

.. autoclass:: TextChannelConverter
    :members:

.. autoclass:: VoiceChannelConverter
    :members:

.. autoclass:: StageChannelConverter
    :members:

.. autoclass:: CategoryChannelConverter
    :members:

.. autoclass:: ForumChannelConverter
    :members:

.. autoclass:: ThreadConverter
    :members:

.. autoclass:: ColourConverter
    :members:

.. autoclass:: RoleConverter
    :members:

.. autoclass:: GameConverter
    :members:

.. autoclass:: InviteConverter
    :members:

.. autoclass:: GuildConverter
    :members:

.. autoclass:: EmojiConverter
    :members:

.. autoclass:: PartialEmojiConverter
    :members:

.. autoclass:: GuildStickerConverter
    :members:

.. autoclass:: PermissionsConverter
    :members:

.. autoclass:: GuildScheduledEventConverter
    :members:

.. autoclass:: clean_content
    :members:

.. autoclass:: Greedy()

.. autofunction:: run_converters

Flag Converter
~~~~~~~~~~~~~~~

.. autoclass:: FlagConverter
    :members:

.. autoclass:: Flag()
    :members:

.. autofunction:: flag

.. _ext_commands_api_errors:

Exceptions
-----------

.. autoexception:: CommandError
    :members:

.. autoexception:: ConversionError
    :members:

.. autoexception:: MissingRequiredArgument
    :members:

.. autoexception:: ArgumentParsingError
    :members:

.. autoexception:: UnexpectedQuoteError
    :members:

.. autoexception:: InvalidEndOfQuotedStringError
    :members:

.. autoexception:: ExpectedClosingQuoteError
    :members:

.. autoexception:: BadArgument
    :members:

.. autoexception:: BadUnionArgument
    :members:

.. autoexception:: BadLiteralArgument
    :members:

.. autoexception:: PrivateMessageOnly
    :members:

.. autoexception:: NoPrivateMessage
    :members:

.. autoexception:: CheckFailure
    :members:

.. autoexception:: CheckAnyFailure
    :members:

.. autoexception:: CommandNotFound
    :members:

.. autoexception:: DisabledCommand
    :members:

.. autoexception:: CommandInvokeError
    :members:

.. autoexception:: TooManyArguments
    :members:

.. autoexception:: UserInputError
    :members:

.. autoexception:: CommandOnCooldown
    :members:

.. autoexception:: MaxConcurrencyReached
    :members:

.. autoexception:: NotOwner
    :members:

.. autoexception:: ObjectNotFound
    :members:

.. autoexception:: MessageNotFound
    :members:

.. autoexception:: MemberNotFound
    :members:

.. autoexception:: GuildNotFound
    :members:

.. autoexception:: UserNotFound
    :members:

.. autoexception:: ChannelNotFound
    :members:

.. autoexception:: ChannelNotReadable
    :members:

.. autoexception:: ThreadNotFound
    :members:

.. autoexception:: BadColourArgument
    :members:

.. autoexception:: RoleNotFound
    :members:

.. autoexception:: BadInviteArgument
    :members:

.. autoexception:: EmojiNotFound
    :members:

.. autoexception:: PartialEmojiConversionFailure
    :members:

.. autoexception:: GuildStickerNotFound
    :members:

.. autoexception:: GuildScheduledEventNotFound
    :members:

.. autoexception:: BadBoolArgument
    :members:

.. autoexception:: LargeIntConversionFailure
    :members:

.. autoexception:: MissingPermissions
    :members:

.. autoexception:: BotMissingPermissions
    :members:

.. autoexception:: MissingRole
    :members:

.. autoexception:: BotMissingRole
    :members:

.. autoexception:: MissingAnyRole
    :members:

.. autoexception:: BotMissingAnyRole
    :members:

.. autoexception:: NSFWChannelRequired
    :members:

.. autoexception:: FlagError
    :members:

.. autoexception:: BadFlagArgument
    :members:

.. autoexception:: MissingFlagArgument
    :members:

.. autoexception:: TooManyFlags
    :members:

.. autoexception:: MissingRequiredFlag
    :members:

.. autoexception:: ExtensionError
    :members:

.. autoexception:: ExtensionAlreadyLoaded
    :members:

.. autoexception:: ExtensionNotLoaded
    :members:

.. autoexception:: NoEntryPointError
    :members:

.. autoexception:: ExtensionFailed
    :members:

.. autoexception:: ExtensionNotFound
    :members:

.. autoexception:: CommandRegistrationError
    :members:


Exception Hierarchy
~~~~~~~~~~~~~~~~~~~~~

.. exception_hierarchy::

    - :exc:`~.DiscordException`
        - :exc:`~.CommandError`
            - :exc:`~.ConversionError`
            - :exc:`~.UserInputError`
                - :exc:`~.MissingRequiredArgument`
                - :exc:`~.TooManyArguments`
                - :exc:`~.BadArgument`
                    - :exc:`~.ObjectNotFound`
                    - :exc:`~.MemberNotFound`
                    - :exc:`~.GuildNotFound`
                    - :exc:`~.UserNotFound`
                    - :exc:`~.MessageNotFound`
                    - :exc:`~.ChannelNotReadable`
                    - :exc:`~.ChannelNotFound`
                    - :exc:`~.ThreadNotFound`
                    - :exc:`~.BadColourArgument`
                    - :exc:`~.RoleNotFound`
                    - :exc:`~.BadInviteArgument`
                    - :exc:`~.EmojiNotFound`
                    - :exc:`~.PartialEmojiConversionFailure`
                    - :exc:`~.GuildStickerNotFound`
                    - :exc:`~.GuildScheduledEventNotFound`
                    - :exc:`~.BadBoolArgument`
                    - :exc:`~.LargeIntConversionFailure`
                    - :exc:`~.FlagError`
                        - :exc:`~.BadFlagArgument`
                        - :exc:`~.MissingFlagArgument`
                        - :exc:`~.TooManyFlags`
                        - :exc:`~.MissingRequiredFlag`
                - :exc:`~.BadUnionArgument`
                - :exc:`~.BadLiteralArgument`
                - :exc:`~.ArgumentParsingError`
                    - :exc:`~.UnexpectedQuoteError`
                    - :exc:`~.InvalidEndOfQuotedStringError`
                    - :exc:`~.ExpectedClosingQuoteError`
            - :exc:`~.CommandNotFound`
            - :exc:`~.CheckFailure`
                - :exc:`~.CheckAnyFailure`
                - :exc:`~.PrivateMessageOnly`
                - :exc:`~.NoPrivateMessage`
                - :exc:`~.NotOwner`
                - :exc:`~.MissingPermissions`
                - :exc:`~.BotMissingPermissions`
                - :exc:`~.MissingRole`
                - :exc:`~.BotMissingRole`
                - :exc:`~.MissingAnyRole`
                - :exc:`~.BotMissingAnyRole`
                - :exc:`~.NSFWChannelRequired`
            - :exc:`~.DisabledCommand`
            - :exc:`~.CommandInvokeError`
            - :exc:`~.CommandOnCooldown`
            - :exc:`~.MaxConcurrencyReached`
        - :exc:`~.ExtensionError`
            - :exc:`~.ExtensionAlreadyLoaded`
            - :exc:`~.ExtensionNotLoaded`
            - :exc:`~.NoEntryPointError`
            - :exc:`~.ExtensionFailed`
            - :exc:`~.ExtensionNotFound`
    - :exc:`~.ClientException`
        - :exc:`~.CommandRegistrationError`

Warnings
----------

.. autoclass:: MessageContentPrefixWarning

Warning Hierarchy
~~~~~~~~~~~~~~~~~~~

.. exception_hierarchy::

    - :class:`~.DiscordWarning`
        - :class:`~.MessageContentPrefixWarning`
