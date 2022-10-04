.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Guild Scheduled Events
======================

This section documents everything related to Guild Scheduled Events.

Classes
-------

GuildScheduledEvent
~~~~~~~~~~~~~~~~~~~~

.. attributetable:: GuildScheduledEvent

.. autoclass:: GuildScheduledEvent()
    :members:

Data Classes
------------

GuildScheduledEventMetadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: GuildScheduledEventMetadata

.. autoclass:: GuildScheduledEventMetadata()
    :members:

RawGuildScheduledEventUserActionEvent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: RawGuildScheduledEventUserActionEvent

.. autoclass:: RawGuildScheduledEventUserActionEvent()
    :members:

Enumerations
------------

GuildScheduledEventEntityType
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. class:: GuildScheduledEventEntityType

    |discord_enum|

    Represents the type of a guild scheduled event entity.

    .. versionadded:: 2.3

    .. attribute:: stage_instance

        The guild scheduled event will take place in a stage channel.

    .. attribute:: voice

        The guild scheduled event will take place in a voice channel.

    .. attribute:: external

        The guild scheduled event will take place in a custom location.

GuildScheduledEventStatus
~~~~~~~~~~~~~~~~~~~~~~~~~

.. class:: GuildScheduledEventStatus

    |discord_enum|

    Represents the status of a guild scheduled event.

    .. versionadded:: 2.3

    .. attribute:: scheduled

        Represents a scheduled event.

    .. attribute:: active

        Represents an active event.

    .. attribute:: completed

        Represents a completed event.

    .. attribute:: canceled

        Represents a canceled event.

    .. attribute:: cancelled

        An alias for :attr:`canceled`.

        .. versionadded:: 2.6

GuildScheduledEventPrivacyLevel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. class:: GuildScheduledEventPrivacyLevel

    |discord_enum|

    Represents the privacy level of a guild scheduled event.

    .. versionadded:: 2.3

    .. attribute:: guild_only

        The guild scheduled event is only for a specific guild.

Events
------

- :func:`disnake.on_guild_scheduled_event_create(event)`
- :func:`disnake.on_guild_scheduled_event_delete(event)`
- :func:`disnake.on_guild_scheduled_event_update(before, after)`
- :func:`disnake.on_guild_scheduled_event_subscribe(event, user)`
- :func:`disnake.on_guild_scheduled_event_unsubscribe(event, user)`
- :func:`disnake.on_raw_guild_scheduled_event_subscribe(payload)`
- :func:`disnake.on_raw_guild_scheduled_event_unsubscribe(payload)`

Check out the :ref:`related events <related_events_guild_scheduled_event>`!
