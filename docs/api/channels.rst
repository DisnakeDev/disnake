.. currentmodule:: disnake

Channels
========

This section documents everything related to channels and threads.

Classes
-------

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

CategoryChannel
~~~~~~~~~~~~~~~~~

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

PartialMessageable
~~~~~~~~~~~~~~~~~~

.. attributetable:: PartialMessageable

.. autoclass:: PartialMessageable()
    :members:
    :inherited-members:

Data Classes
------------

ChannelFlags
~~~~~~~~~~~~

.. attributetable:: ChannelFlags

.. autoclass:: ChannelFlags
    :members:

VoiceRegion
~~~~~~~~~~~

.. attributetable:: VoiceRegion

.. autoclass:: VoiceRegion()
    :members:

RawThreadDeleteEvent
~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: RawThreadDeleteEvent

.. autoclass:: RawThreadDeleteEvent()
    :members:

RawThreadMemberRemoveEvent
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: RawThreadMemberRemoveEvent

.. autoclass:: RawThreadMemberRemoveEvent()
    :members:

Enumerations
------------

ChannelType
~~~~~~~~~~~

.. class:: ChannelType

    |discord_enum|

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

    |discord_enum|

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

    |discord_enum|

    Represents the camera video quality mode for voice channel participants.

    .. versionadded:: 2.0

    .. attribute:: auto

        Represents auto camera video quality.

    .. attribute:: full

        Represents full camera video quality.

Events
------

.. function:: on_guild_channel_delete(channel)
              on_guild_channel_create(channel)

    |discord_events|

    Called whenever a guild channel is deleted or created.

    Note that you can get the guild from :attr:`~abc.GuildChannel.guild`.

    This requires :attr:`Intents.guilds` to be enabled.

    :param channel: The guild channel that got created or deleted.
    :type channel: :class:`abc.GuildChannel`

.. function:: on_guild_channel_update(before, after)

    |discord_event|

    Called whenever a guild channel is updated. e.g. changed name, topic, permissions.

    This requires :attr:`Intents.guilds` to be enabled.

    :param before: The updated guild channel's old info.
    :type before: :class:`abc.GuildChannel`
    :param after: The updated guild channel's new info.
    :type after: :class:`abc.GuildChannel`

.. function:: on_guild_channel_pins_update(channel, last_pin)

    |discord_event|

    Called whenever a message is pinned or unpinned from a guild channel.

    This requires :attr:`Intents.guilds` to be enabled.

    :param channel: The guild channel that had its pins updated.
    :type channel: Union[:class:`abc.GuildChannel`, :class:`Thread`]
    :param last_pin: The latest message that was pinned as an aware datetime in UTC. Could be ``None``.
    :type last_pin: Optional[:class:`datetime.datetime`]

.. function:: on_private_channel_update(before, after)

    |discord_event|

    Called whenever a private group DM is updated. e.g. changed name or topic.

    This requires :attr:`Intents.messages` to be enabled.

    :param before: The updated group channel's old info.
    :type before: :class:`GroupChannel`
    :param after: The updated group channel's new info.
    :type after: :class:`GroupChannel`

.. function:: on_private_channel_pins_update(channel, last_pin)

    |discord_event|

    Called whenever a message is pinned or unpinned from a private channel.

    :param channel: The private channel that had its pins updated.
    :type channel: :class:`abc.PrivateChannel`
    :param last_pin: The latest message that was pinned as an aware datetime in UTC. Could be ``None``.
    :type last_pin: Optional[:class:`datetime.datetime`]

.. function:: on_thread_create(thread)

    |discord_event|

    Called whenever a thread is created.

    Note that you can get the guild from :attr:`Thread.guild`.

    This requires :attr:`Intents.guilds` to be enabled.

    .. note::
        This only works for threads created in channels the bot already has access to,
        and only for public threads unless the bot has the :attr:`~Permissions.manage_threads` permission.

    .. versionadded:: 2.5

    :param thread: The thread that got created.
    :type thread: :class:`Thread`

.. function:: on_thread_join(thread)

    |discord_event|

    Called whenever the bot joins a thread or gets access to a thread
    (for example, by gaining access to the parent channel).

    Note that you can get the guild from :attr:`Thread.guild`.

    This requires :attr:`Intents.guilds` to be enabled.

    .. note::
        This event will not be called for threads created by the bot or
        threads created on one of the bot's messages.

    .. versionadded:: 2.0

    .. versionchanged:: 2.5
        This is no longer being called when a thread is created, see :func:`on_thread_create` instead.

    :param thread: The thread that got joined.
    :type thread: :class:`Thread`

.. function:: on_thread_member_join(member)
              on_thread_member_remove(member)

    |discord_events|

    Called when a :class:`ThreadMember` leaves or joins a :class:`Thread`.

    You can get the thread a member belongs in by accessing :attr:`ThreadMember.thread`.

    On removal events, if the member being removed is not found in the internal cache,
    then this event will not be called. Consider using :func:`on_raw_thread_member_remove` instead.

    This requires :attr:`Intents.members` to be enabled.

    .. versionadded:: 2.0

    :param member: The member who joined or left.
    :type member: :class:`ThreadMember`

.. function:: on_thread_remove(thread)

    |discord_event|

    Called whenever a thread is removed. This is different from a thread being deleted.

    Note that you can get the guild from :attr:`Thread.guild`.

    This requires :attr:`Intents.guilds` to be enabled.

    .. warning::

        Due to technical limitations, this event might not be called
        as soon as one expects. Since the library tracks thread membership
        locally, the API only sends updated thread membership status upon being
        synced by joining a thread.

    .. versionadded:: 2.0

    :param thread: The thread that got removed.
    :type thread: :class:`Thread`

.. function:: on_thread_update(before, after)

    |discord_event|

    Called when a thread is updated. If the thread is not found
    in the internal thread cache, then this event will not be called.
    Consider using :func:`on_raw_thread_update` which will be called regardless of the cache.

    This requires :attr:`Intents.guilds` to be enabled.

    .. versionadded:: 2.0

    :param before: The updated thread's old info.
    :type before: :class:`Thread`
    :param after: The updated thread's new info.
    :type after: :class:`Thread`

.. function:: on_thread_delete(thread)

    |discord_event|

    Called when a thread is deleted. If the thread is not found
    in the internal thread cache, then this event will not be called.
    Consider using :func:`on_raw_thread_delete` instead.

    Note that you can get the guild from :attr:`Thread.guild`.

    This requires :attr:`Intents.guilds` to be enabled.

    .. versionadded:: 2.0

    :param thread: The thread that got deleted.
    :type thread: :class:`Thread`

.. function:: on_raw_thread_member_remove(payload)

    |discord_event|

    Called when a :class:`ThreadMember` leaves :class:`Thread`.
    Unlike :func:`on_thread_member_remove`, this is called regardless of the thread member cache.

    You can get the thread a member belongs in by accessing :attr:`ThreadMember.thread`.

    This requires :attr:`Intents.members` to be enabled.

    .. versionadded:: 2.5

    :param payload: The raw event payload data.
    :type payload: :class:`RawThreadMemberRemoveEvent`

.. function:: on_raw_thread_update(after)

    |discord_event|

    Called whenever a thread is updated.
    Unlike :func:`on_thread_update`, this is called
    regardless of the state of the internal thread cache.

    This requires :attr:`Intents.guilds` to be enabled.

    .. versionadded:: 2.5

    :param thread: The updated thread.
    :type thread: :class:`Thread`

.. function:: on_raw_thread_delete(payload)

    |discord_event|

    Called whenever a thread is deleted.
    Unlike :func:`on_thread_delete`, this is called
    regardless of the state of the internal thread cache.

    Note that you can get the guild from :attr:`Thread.guild`.

    This requires :attr:`Intents.guilds` to be enabled.

    .. versionadded:: 2.5

    :param payload: The raw event payload data.
    :type payload: :class:`RawThreadDeleteEvent`
