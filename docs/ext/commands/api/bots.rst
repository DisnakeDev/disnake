.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake.ext.commands

.. _ext_commands_api_bots:

Bots
====

This section documents everything related to bots - specialized :class:`disnake.Client`\s
whose purpose is to streamline and simplify development of (application) commands.

Classes
-------

Bot
~~~

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
~~~~~~~~~~~~~~

.. attributetable:: AutoShardedBot

.. autoclass:: AutoShardedBot
    :members:

InteractionBot
~~~~~~~~~~~~~~

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
