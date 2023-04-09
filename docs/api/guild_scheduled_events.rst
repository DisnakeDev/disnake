.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Guild Scheduled Events
======================

This section documents everything related to Guild Scheduled Events.

Discord Models
---------------

GuildScheduledEvent
~~~~~~~~~~~~~~~~~~~

.. attributetable:: GuildScheduledEvent

.. autoclass:: GuildScheduledEvent()
    :members:

RawGuildScheduledEventUserActionEvent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: RawGuildScheduledEventUserActionEvent

.. autoclass:: RawGuildScheduledEventUserActionEvent()
    :members:

Data Classes
------------

GuildScheduledEventMetadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: GuildScheduledEventMetadata

.. autoclass:: GuildScheduledEventMetadata
    :members:

Enumerations
------------

GuildScheduledEventEntityType
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. class:: GuildScheduledEventEntityType

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

    Represents the privacy level of a guild scheduled event.

    .. versionadded:: 2.3

    .. attribute:: guild_only

        The guild scheduled event is only for a specific guild.

Events
------

- :func:`on_guild_scheduled_event_create(event) <disnake.on_guild_scheduled_event_create>`
- :func:`on_guild_scheduled_event_delete(event) <disnake.on_guild_scheduled_event_delete>`
- :func:`on_guild_scheduled_event_update(before, after) <disnake.on_guild_scheduled_event_update>`
- :func:`on_guild_scheduled_event_subscribe(event, user) <disnake.on_guild_scheduled_event_subscribe>`
- :func:`on_guild_scheduled_event_unsubscribe(event, user) <disnake.on_guild_scheduled_event_unsubscribe>`
- :func:`on_raw_guild_scheduled_event_subscribe(payload) <disnake.on_raw_guild_scheduled_event_subscribe>`
- :func:`on_raw_guild_scheduled_event_unsubscribe(payload) <disnake.on_raw_guild_scheduled_event_unsubscribe>`
