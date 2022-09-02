.. currentmodule:: disnake.ext.commands

Application Commands
====================

This section documents everything about handling application commands with this extension.

Classes
-------

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

Events
------

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

Functions
---------

.. autofunction:: slash_command
    :decorator:

.. autofunction:: user_command
    :decorator:

.. autofunction:: message_command
    :decorator:

.. autofunction:: Param

.. autofunction:: option_enum

.. autofunction:: inject

.. autofunction:: register_injection
    :decorator:
