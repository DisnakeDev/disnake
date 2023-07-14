.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Channels
========

This section documents everything related to channels and threads.

Discord Models
---------------

TextChannel
~~~~~~~~~~~

.. attributetable:: TextChannel

.. autoclass:: TextChannel()
    :members:
    :inherited-members:
    :exclude-members: history, typing

    .. automethod:: history
        :async-for:

    .. automethod:: typing
        :async-with:

VoiceChannel
~~~~~~~~~~~~

.. attributetable:: VoiceChannel

.. autoclass:: VoiceChannel()
    :members:
    :inherited-members:
    :exclude-members: pins

CategoryChannel
~~~~~~~~~~~~~~~

.. attributetable:: CategoryChannel

.. autoclass:: CategoryChannel()
    :members:
    :inherited-members:

Thread
~~~~~~

.. attributetable:: Thread

.. autoclass:: Thread()
    :members:
    :inherited-members:
    :exclude-members: history, typing

    .. automethod:: history
        :async-for:

    .. automethod:: typing
        :async-with:

ThreadMember
~~~~~~~~~~~~

.. attributetable:: ThreadMember

.. autoclass:: ThreadMember()
    :members:

StageChannel
~~~~~~~~~~~~

.. attributetable:: StageChannel

.. autoclass:: StageChannel()
    :members:
    :inherited-members:
    :exclude-members: pins

ForumChannel
~~~~~~~~~~~~

.. attributetable:: ForumChannel

.. autoclass:: ForumChannel()
    :members:
    :inherited-members:
    :exclude-members: typing

    .. automethod:: typing
        :async-with:

DMChannel
~~~~~~~~~

.. attributetable:: DMChannel

.. autoclass:: DMChannel()
    :members:
    :inherited-members:
    :exclude-members: history, typing

    .. automethod:: history
        :async-for:

    .. automethod:: typing
        :async-with:

GroupChannel
~~~~~~~~~~~~

.. attributetable:: GroupChannel

.. autoclass:: GroupChannel()
    :members:
    :inherited-members:
    :exclude-members: history, typing

    .. automethod:: history
        :async-for:

    .. automethod:: typing
        :async-with:

RawThreadDeleteEvent
~~~~~~~~~~~~~~~~~~~~

.. attributetable:: RawThreadDeleteEvent

.. autoclass:: RawThreadDeleteEvent()
    :members:

RawThreadMemberRemoveEvent
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: RawThreadMemberRemoveEvent

.. autoclass:: RawThreadMemberRemoveEvent()
    :members:

Data Classes
------------

PartialMessageable
~~~~~~~~~~~~~~~~~~

.. attributetable:: PartialMessageable

.. autoclass:: PartialMessageable()
    :members:
    :inherited-members:

ChannelFlags
~~~~~~~~~~~~

.. attributetable:: ChannelFlags

.. autoclass:: ChannelFlags
    :members:

ForumTag
~~~~~~~~

.. attributetable:: ForumTag

.. autoclass:: ForumTag()
    :members:
    :inherited-members:

Enumerations
------------

ChannelType
~~~~~~~~~~~

.. class:: ChannelType

    Specifies the type of channel.

    .. attribute:: text

        A text channel.
    .. attribute:: voice

        A voice channel.
    .. attribute:: private

        A private text channel. Also called a direct message.
    .. attribute:: group

        A private group text channel.
    .. attribute:: category

        A category channel.
    .. attribute:: news

        A guild news channel.

    .. attribute:: stage_voice

        A guild stage voice channel.

        .. versionadded:: 1.7

    .. attribute:: news_thread

        A news thread.

        .. versionadded:: 2.0

    .. attribute:: public_thread

        A public thread.

        .. versionadded:: 2.0

    .. attribute:: private_thread

        A private thread.

        .. versionadded:: 2.0

    .. attribute:: guild_directory

        A student hub channel.

        .. versionadded:: 2.1

    .. attribute:: forum

        A channel of only threads.

        .. versionadded:: 2.5

ThreadArchiveDuration
~~~~~~~~~~~~~~~~~~~~~

.. class:: ThreadArchiveDuration

    Represents the automatic archive duration of a thread in minutes.

    .. versionadded:: 2.3

    .. attribute:: hour

        The thread will archive after an hour of inactivity.

    .. attribute:: day

        The thread will archive after a day of inactivity.

    .. attribute:: three_days

        The thread will archive after three days of inactivity.

    .. attribute:: week

        The thread will archive after a week of inactivity.

VideoQualityMode
~~~~~~~~~~~~~~~~

.. class:: VideoQualityMode

    Represents the camera video quality mode for voice channel participants.

    .. versionadded:: 2.0

    .. attribute:: auto

        Represents auto camera video quality.

    .. attribute:: full

        Represents full camera video quality.

ThreadSortOrder
~~~~~~~~~~~~~~~

.. class:: ThreadSortOrder

    Represents the sort order of threads in :class:`ForumChannel`\s.

    .. versionadded:: 2.6

    .. attribute:: latest_activity

        Sort forum threads by activity.

    .. attribute:: creation_date

        Sort forum threads by creation date/time (from newest to oldest).

ThreadLayout
~~~~~~~~~~~~

.. class:: ThreadLayout

    Represents the layout of threads in :class:`ForumChannel`\s.

    .. versionadded:: 2.8

    .. attribute:: not_set

        No preferred layout has been set.

    .. attribute:: list_view

        Display forum threads in a text-focused list.

    .. attribute:: gallery_view

        Display forum threads in a media-focused collection of tiles.

Events
------

- :func:`on_guild_channel_create(channel) <disnake.on_guild_channel_create>`
- :func:`on_guild_channel_delete(channel) <disnake.on_guild_channel_delete>`
- :func:`on_guild_channel_update(before, after) <disnake.on_guild_channel_update>`
- :func:`on_guild_channel_pins_update(channel, last_pin) <disnake.on_guild_channel_pins_update>`
- :func:`on_private_channel_update(before, after) <disnake.on_private_channel_update>`
- :func:`on_private_channel_pins_update(channel, last_pin) <disnake.on_private_channel_pins_update>`
- :func:`on_thread_create(thread) <disnake.on_thread_create>`
- :func:`on_thread_update(before, after) <disnake.on_thread_update>`
- :func:`on_thread_delete(thread) <disnake.on_thread_delete>`
- :func:`on_thread_join(thread) <disnake.on_thread_join>`
- :func:`on_thread_remove(thread) <disnake.on_thread_remove>`
- :func:`on_thread_member_join(member) <disnake.on_thread_member_join>`
- :func:`on_thread_member_remove(member) <disnake.on_thread_member_remove>`
- :func:`on_raw_thread_member_remove(payload) <disnake.on_raw_thread_member_remove>`
- :func:`on_raw_thread_update(after) <disnake.on_raw_thread_update>`
- :func:`on_raw_thread_delete(payload) <disnake.on_raw_thread_delete>`
