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

MediaChannel
~~~~~~~~~~~~

.. attributetable:: MediaChannel

.. autoclass:: MediaChannel()
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

ThreadWithMessage
~~~~~~~~~~~~~~~~~

.. class:: ThreadWithMessage

    A :class:`~typing.NamedTuple` which represents a thread and message returned from :meth:`ForumChannel.create_thread`.

    .. attribute:: thread

        The created thread.

        :type: :class:`Thread`
    .. attribute:: message

        The initial message in the thread.

        :type: :class:`Message`

Enumerations
------------

ChannelType
~~~~~~~~~~~

.. autoclass:: ChannelType()
    :members:

ThreadArchiveDuration
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ThreadArchiveDuration()
    :members:

VideoQualityMode
~~~~~~~~~~~~~~~~

.. autoclass:: VideoQualityMode()
    :members:

ThreadSortOrder
~~~~~~~~~~~~~~~

.. autoclass:: ThreadSortOrder()
    :members:

ThreadLayout
~~~~~~~~~~~~

.. autoclass:: ThreadLayout()
    :members:

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
