.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Application Commands
====================

This section documents everything related to Discord's
:ddocs:`application commands <interactions/application-commands>`.

Discord Models
---------------

APISlashCommand
~~~~~~~~~~~~~~~

.. attributetable:: APISlashCommand

.. autoclass:: APISlashCommand()
    :members:
    :inherited-members:

APIUserCommand
~~~~~~~~~~~~~~

.. attributetable:: APIUserCommand

.. autoclass:: APIUserCommand()
    :members:
    :inherited-members:

APIMessageCommand
~~~~~~~~~~~~~~~~~

.. attributetable:: APIMessageCommand

.. autoclass:: APIMessageCommand()
    :members:
    :inherited-members:

ApplicationCommandPermissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: ApplicationCommandPermissions

.. autoclass:: ApplicationCommandPermissions()
    :members:

GuildApplicationCommandPermissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: GuildApplicationCommandPermissions

.. autoclass:: GuildApplicationCommandPermissions()
    :members:

Data Classes
------------

ApplicationCommand
~~~~~~~~~~~~~~~~~~

.. attributetable:: ApplicationCommand

.. autoclass:: ApplicationCommand()
    :members:

SlashCommand
~~~~~~~~~~~~

.. attributetable:: SlashCommand

.. autoclass:: SlashCommand()
    :members:
    :inherited-members:

UserCommand
~~~~~~~~~~~

.. attributetable:: UserCommand

.. autoclass:: UserCommand()
    :members:
    :inherited-members:

MessageCommand
~~~~~~~~~~~~~~

.. attributetable:: MessageCommand

.. autoclass:: MessageCommand()
    :members:
    :inherited-members:

Option
~~~~~~

.. attributetable:: Option

.. autoclass:: Option()
    :members:

OptionChoice
~~~~~~~~~~~~

.. attributetable:: OptionChoice

.. autoclass:: OptionChoice()
    :members:

Enumerations
------------

OptionType
~~~~~~~~~~

.. class:: OptionType

    Represents the type of an option.

    .. versionadded:: 2.1

    .. attribute:: sub_command

        Represents a sub command of the main command or group.
    .. attribute:: sub_command_group

        Represents a sub command group of the main command.
    .. attribute:: string

        Represents a string option.
    .. attribute:: integer

        Represents an integer option.
    .. attribute:: boolean

        Represents a boolean option.
    .. attribute:: user

        Represents a user option.
    .. attribute:: channel

        Represents a channel option.
    .. attribute:: role

        Represents a role option.
    .. attribute:: mentionable

        Represents a role + user option.
    .. attribute:: number

        Represents a float option.
    .. attribute:: attachment

        Represents an attachment option.

        .. versionadded:: 2.4

ApplicationCommandType
~~~~~~~~~~~~~~~~~~~~~~

.. class:: ApplicationCommandType

    Represents the type of an application command.

    .. versionadded:: 2.1

    .. attribute:: chat_input

        Represents a slash command.
    .. attribute:: user

        Represents a user command from the context menu.
    .. attribute:: message

        Represents a message command from the context menu.

ApplicationCommandPermissionType
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. class:: ApplicationCommandPermissionType

    Represents the type of a permission of an application command.

    .. versionadded:: 2.5

    .. attribute:: role

        Represents a permission that affects roles.
    .. attribute:: user

        Represents a permission that affects users.
    .. attribute:: channel

        Represents a permission that affects channels.

Events
------

- :func:`on_application_command_permissions_update(permissions) <disnake.on_application_command_permissions_update>`
