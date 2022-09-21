.. currentmodule:: disnake

Integrations
============

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

Check out the :ref:`related events <related_events_integration>`!
