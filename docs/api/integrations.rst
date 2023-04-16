.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Integrations
============

This section documents everything related to Integrations - special entities integrated into :class:`Guild`\s.
Most common examples are bots and Twitch/YouTube integrations.

Discord Models
---------------

Integration
~~~~~~~~~~~

.. autoclass:: Integration()
    :members:
    :inherited-members:

IntegrationAccount
~~~~~~~~~~~~~~~~~~

.. autoclass:: IntegrationAccount()
    :members:

BotIntegration
~~~~~~~~~~~~~~

.. autoclass:: BotIntegration()
    :members:
    :inherited-members:

IntegrationApplication
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: IntegrationApplication()
    :members:

StreamIntegration
~~~~~~~~~~~~~~~~~

.. autoclass:: StreamIntegration()
    :members:
    :inherited-members:

PartialIntegration
~~~~~~~~~~~~~~~~~~

.. autoclass:: PartialIntegration()
    :members:

Data Classes
------------

RawIntegrationDeleteEvent
~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: RawIntegrationDeleteEvent

.. autoclass:: RawIntegrationDeleteEvent()
    :members:


Enumerations
------------

ExpireBehaviour
~~~~~~~~~~~~~~~

.. class:: ExpireBehaviour

    Represents the behaviour the :class:`Integration` should perform
    when a user's subscription has finished.

    There is an alias for this called ``ExpireBehavior``.

    .. versionadded:: 1.4

    .. attribute:: remove_role

        This will remove the :attr:`StreamIntegration.role` from the user
        when their subscription is finished.

    .. attribute:: kick

        This will kick the user when their subscription is finished.

Events
------

- :func:`on_guild_integrations_update(guild) <disnake.on_guild_integrations_update>`
- :func:`on_integration_create(integration) <disnake.on_integration_create>`
- :func:`on_integration_update(integration) <disnake.on_integration_update>`
- :func:`on_raw_integration_delete(payload) <disnake.on_raw_integration_delete>`
