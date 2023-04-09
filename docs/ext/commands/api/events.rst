.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake.ext.commands

Events
======

This section documents events related to the commands extension.

These events function similar to :ref:`the regular events <disnake_api_events>`, except they
are custom to the command extension module.

Prefix Commands
---------------

.. function:: on_command(ctx)

    An event that is called when a command is found and is about to be invoked.

    This event is called regardless of whether the command itself succeeds via
    error or completes.

    :param ctx: The invocation context.
    :type ctx: :class:`.Context`

.. function:: on_command_completion(ctx)

    An event that is called when a command has completed its invocation.

    This event is called only if the command succeeded, i.e. all checks have
    passed and the user input it correctly.

    :param ctx: The invocation context.
    :type ctx: :class:`.Context`

.. function:: on_command_error(ctx, error)

    An error handler that is called when an error is raised
    inside a command either through user input error, check
    failure, or an error in your own code.

    A default one is provided (:meth:`.Bot.on_command_error`).

    :param ctx: The invocation context.
    :type ctx: :class:`.Context`
    :param error: The error that was raised.
    :type error: :class:`.CommandError` derived

Application Commands
--------------------

.. function:: on_slash_command(inter)

    An event that is called when a slash command is found and is about to be invoked.

    This event is called regardless of whether the slash command itself succeeds via
    error or completes.

    :param inter: The interaction that invoked this slash command.
    :type inter: :class:`.ApplicationCommandInteraction`

.. function:: on_slash_command_completion(inter)

    An event that is called when a slash command has completed its invocation.

    This event is called only if the slash command succeeded, i.e. all checks have
    passed and command handler ran successfully.

    :param inter: The interaction that invoked this slash command.
    :type inter: :class:`.ApplicationCommandInteraction`

.. function:: on_slash_command_error(inter, error)

    An error handler that is called when an error is raised
    inside a slash command either through user input error, check
    failure, or an error in your own code.

    A default one is provided (:meth:`.Bot.on_slash_command_error`).

    :param inter: The interaction that invoked this slash command.
    :type inter: :class:`.ApplicationCommandInteraction`
    :param error: The error that was raised.
    :type error: :class:`.CommandError` derived

.. function:: on_user_command(inter)

    An event that is called when a user command is found and is about to be invoked.

    This event is called regardless of whether the user command itself succeeds via
    error or completes.

    :param inter: The interaction that invoked this user command.
    :type inter: :class:`.ApplicationCommandInteraction`

.. function:: on_user_command_completion(inter)

    An event that is called when a user command has completed its invocation.

    This event is called only if the user command succeeded, i.e. all checks have
    passed and command handler ran successfully.

    :param inter: The interaction that invoked this user command.
    :type inter: :class:`.ApplicationCommandInteraction`

.. function:: on_user_command_error(inter, error)

    An error handler that is called when an error is raised
    inside a user command either through check
    failure, or an error in your own code.

    A default one is provided (:meth:`.Bot.on_user_command_error`).

    :param inter: The interaction that invoked this user command.
    :type inter: :class:`.ApplicationCommandInteraction`
    :param error: The error that was raised.
    :type error: :class:`.CommandError` derived

.. function:: on_message_command(inter)

    An event that is called when a message command is found and is about to be invoked.

    This event is called regardless of whether the message command itself succeeds via
    error or completes.

    :param inter: The interaction that invoked this message command.
    :type inter: :class:`.ApplicationCommandInteraction`

.. function:: on_message_command_completion(inter)

    An event that is called when a message command has completed its invocation.

    This event is called only if the message command succeeded, i.e. all checks have
    passed and command handler ran successfully.

    :param inter: The interaction that invoked this message command.
    :type inter: :class:`.ApplicationCommandInteraction`

.. function:: on_message_command_error(inter, error)

    An error handler that is called when an error is raised
    inside a message command either through check
    failure, or an error in your own code.

    A default one is provided (:meth:`.Bot.on_message_command_error`).

    :param inter: The interaction that invoked this message command.
    :type inter: :class:`.ApplicationCommandInteraction`
    :param error: The error that was raised.
    :type error: :class:`.CommandError` derived
