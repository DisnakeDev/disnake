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

.. autoclass:: Option
    :members:

OptionChoice
~~~~~~~~~~~~

.. attributetable:: OptionChoice

.. autoclass:: OptionChoice()
    :members:

ApplicationInstallTypes
~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: ApplicationInstallTypes

.. autoclass:: ApplicationInstallTypes()
    :members:

InteractionContextTypes
~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: InteractionContextTypes

.. autoclass:: InteractionContextTypes()
    :members:

Enumerations
------------

OptionType
~~~~~~~~~~

.. autoclass:: OptionType()
    :members:

ApplicationCommandType
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ApplicationCommandType()
    :members:

ApplicationCommandPermissionType
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ApplicationCommandPermissionType()
    :members:

Events
------

- :func:`on_application_command_permissions_update(permissions) <disnake.on_application_command_permissions_update>`
