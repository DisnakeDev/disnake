.. currentmodule:: disnake

Integration
===========

This section documents everything related to Integrations - special entities integrated into :class:`Guilds <Guild>`.
Most common examples are Twitch/YouTube integrations and application commands bots (applications invited with ``applications.commands``
:attr:`scope <InstallParams.scopes>`).

Classes
-------

Integration
~~~~~~~~~~~~

.. autoclass:: Integration()
    :members:
    :inherited-members:

.. autoclass:: IntegrationAccount()
    :members:

.. autoclass:: BotIntegration()
    :members:
    :inherited-members:

.. autoclass:: IntegrationApplication()
    :members:

.. autoclass:: StreamIntegration()
    :members:
    :inherited-members:

.. autoclass:: PartialIntegration()
    :members:

Data Classes
------------

RawIntegrationDeleteEvent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: RawIntegrationDeleteEvent

.. autoclass:: RawIntegrationDeleteEvent()
    :members:


Enumerations
------------

ExpireBehaviour
~~~~~~~~~~~~~~~

.. class:: ExpireBehaviour

    |discord_enum|

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

.. function:: on_guild_integrations_update(guild)

    |discord_event|

    Called whenever an integration is created, modified, or removed from a guild.

    This requires :attr:`Intents.integrations` to be enabled.

    .. versionadded:: 1.4

    :param guild: The guild that had its integrations updated.
    :type guild: :class:`Guild`

.. function:: on_integration_create(integration)

    |discord_event|

    Called when an integration is created.

    This requires :attr:`Intents.integrations` to be enabled.

    .. versionadded:: 2.0

    :param integration: The integration that was created.
    :type integration: :class:`Integration`

.. function:: on_integration_update(integration)

    |discord_event|

    Called when an integration is updated.

    This requires :attr:`Intents.integrations` to be enabled.

    .. versionadded:: 2.0

    :param integration: The integration that was updated.
    :type integration: :class:`Integration`

.. function:: on_raw_integration_delete(payload)

    |discord_event|

    Called when an integration is deleted.

    This requires :attr:`Intents.integrations` to be enabled.

    .. versionadded:: 2.0

    :param payload: The raw event payload data.
    :type payload: :class:`RawIntegrationDeleteEvent`
