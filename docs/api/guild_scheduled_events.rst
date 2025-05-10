.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Guild Scheduled Events
======================

This section documents everything related to Guild Scheduled Events.

Discord Models
---------------

GuildScheduledEventRecurrenceRule
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: GuildScheduledEventRecurrenceRule

.. autoclass:: GuildScheduledEventRecurrenceRule()
    :members:

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

GuildScheduledEventNWeekday
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: GuildScheduledEventNWeekday

.. autoclass:: GuildScheduledEventNWeekday
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

GuildScheduledEventFrequency
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. class:: GuildScheduledEventFrequency

    Represents the frequency of recurrence for a scheduled event.

    This determines how often the event should repeat, such as daily, weekly, monthly, or yearly.

    .. versionadded:: 2.11

    .. attribute:: YEARLY

        The event occurs once a year.

    .. attribute:: MONTHLY

        The event occurs once a month.

    .. attribute:: WEEKLY

        The event occurs once a week.

    .. attribute:: DAILY

        The event occurs every day.

GuildScheduledEventWeekday
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. class:: GuildScheduledEventWeekday

    Represents the day of the week used in recurrence rules.

    Used for specifying which days an event should recur on.

    .. versionadded:: 2.11

    .. attribute:: MONDAY

        Monday.

    .. attribute:: TUESDAY

        Tuesday.

    .. attribute:: WEDNESDAY

        Wednesday.

    .. attribute:: THURSDAY

        Thursday.

    .. attribute:: FRIDAY

        Friday.

    .. attribute:: SATURDAY

        Saturday.

    .. attribute:: SUNDAY

        Sunday.

GuildScheduledEventMonth
~~~~~~~~~~~~~~~~~~~~~~~~

.. class:: GuildScheduledEventMonth

    Represents the month of the year used in recurrence rules.

    Used for specifying which months an event should recur on.

    .. versionadded:: 2.11

    .. attribute:: JANUARY

        January.

    .. attribute:: FEBRUARY

        February.

    .. attribute:: MARCH

        March.

    .. attribute:: APRIL

        April.

    .. attribute:: MAY

        May.

    .. attribute:: JUNE

        June.

    .. attribute:: JULY

        July.

    .. attribute:: AUGUST

        August.

    .. attribute:: SEPTEMBER

        September.

    .. attribute:: OCTOBER

        October.

    .. attribute:: NOVEMBER

        November.

    .. attribute:: DECEMBER

        December.

Events
------

- :func:`on_guild_scheduled_event_create(event) <disnake.on_guild_scheduled_event_create>`
- :func:`on_guild_scheduled_event_delete(event) <disnake.on_guild_scheduled_event_delete>`
- :func:`on_guild_scheduled_event_update(before, after) <disnake.on_guild_scheduled_event_update>`
- :func:`on_guild_scheduled_event_subscribe(event, user) <disnake.on_guild_scheduled_event_subscribe>`
- :func:`on_guild_scheduled_event_unsubscribe(event, user) <disnake.on_guild_scheduled_event_unsubscribe>`
- :func:`on_raw_guild_scheduled_event_subscribe(payload) <disnake.on_raw_guild_scheduled_event_subscribe>`
- :func:`on_raw_guild_scheduled_event_unsubscribe(payload) <disnake.on_raw_guild_scheduled_event_unsubscribe>`
