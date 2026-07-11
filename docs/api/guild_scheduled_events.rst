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

.. autoclass:: GuildScheduledEventEntityType()
    :members:

GuildScheduledEventStatus
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: GuildScheduledEventStatus()
    :members:

GuildScheduledEventPrivacyLevel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: GuildScheduledEventPrivacyLevel()
    :members:

Events
------

- :func:`on_guild_scheduled_event_create(event) <disnake.on_guild_scheduled_event_create>`
- :func:`on_guild_scheduled_event_delete(event) <disnake.on_guild_scheduled_event_delete>`
- :func:`on_guild_scheduled_event_update(before, after) <disnake.on_guild_scheduled_event_update>`
- :func:`on_guild_scheduled_event_subscribe(event, user) <disnake.on_guild_scheduled_event_subscribe>`
- :func:`on_guild_scheduled_event_unsubscribe(event, user) <disnake.on_guild_scheduled_event_unsubscribe>`
- :func:`on_raw_guild_scheduled_event_subscribe(payload) <disnake.on_raw_guild_scheduled_event_subscribe>`
- :func:`on_raw_guild_scheduled_event_unsubscribe(payload) <disnake.on_raw_guild_scheduled_event_unsubscribe>`
