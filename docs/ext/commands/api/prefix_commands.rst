.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake.ext.commands

.. _ext_commands_api_prefix_commands:

Prefix Commands
===============

This section documents everything related to prefix commands.

Classes
-------

Command
~~~~~~~

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
~~~~~

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
~~~~~~~~~~

.. attributetable:: GroupMixin

.. autoclass:: GroupMixin
    :members:
    :exclude-members: command, group

    .. automethod:: GroupMixin.command(*args, **kwargs)
        :decorator:

    .. automethod:: GroupMixin.group(*args, **kwargs)
        :decorator:

Functions
---------

.. autofunction:: command
    :decorator:

.. autofunction:: group
    :decorator:

.. autofunction:: when_mentioned

.. autofunction:: when_mentioned_or

Events
------

- :func:`on_command_error(ctx, error) <.on_command_error>`
- :func:`on_command(ctx) <.on_command>`
- :func:`on_command_completion(ctx) <.on_command_completion>`
