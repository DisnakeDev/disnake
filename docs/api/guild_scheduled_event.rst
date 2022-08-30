.. currentmodule:: disnake

Guild Scheduled Event
=====================

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

.. function:: on_guild_scheduled_event_create(event)
              on_guild_scheduled_event_delete(event)

    |discord_events|

    Called when a guild scheduled event is created or deleted.

    This requires :attr:`Intents.guild_scheduled_events` to be enabled.

    .. versionadded:: 2.3

    :param event: The guild scheduled event that was created or deleted.
    :type event: :class:`GuildScheduledEvent`

.. function:: on_guild_scheduled_event_update(before, after)

    |discord_event|

    Called when a guild scheduled event is updated.
    The guild must have existed in the :attr:`Client.guilds` cache.

    This requires :attr:`Intents.guild_scheduled_events` to be enabled.

    .. versionadded:: 2.3

    :param before: The guild scheduled event before the update.
    :type before: :class:`GuildScheduledEvent`
    :param after: The guild scheduled event after the update.
    :type after: :class:`GuildScheduledEvent`

.. function:: on_guild_scheduled_event_subscribe(event, user)
              on_guild_scheduled_event_unsubscribe(event, user)

    |discord_events|

    Called when a user subscribes to or unsubscribes from a guild scheduled event.

    This requires :attr:`Intents.guild_scheduled_events` and :attr:`Intents.members` to be enabled.

    .. versionadded:: 2.3

    :param event: The guild scheduled event that the user subscribed to or unsubscribed from.
    :type event: :class:`GuildScheduledEvent`
    :param user: The user who subscribed to or unsubscribed from the event.
    :type user: Union[:class:`Member`, :class:`User`]

.. function:: on_raw_guild_scheduled_event_subscribe(payload)
              on_raw_guild_scheduled_event_unsubscribe(payload)

    |discord_events|

    Called when a user subscribes to or unsubscribes from a guild scheduled event.
    Unlike :func:`on_guild_scheduled_event_subscribe` and :func:`on_guild_scheduled_event_unsubscribe`,
    this is called regardless of the guild scheduled event cache.

    :param payload: The raw event payload data.
    :type payload: :class:`RawGuildScheduledEventUserActionEvent`
