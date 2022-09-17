.. currentmodule:: disnake

API Reference
===============

The following section outlines the API of disnake.

.. note::

    This module uses the Python logging module to log diagnostic and errors
    in an output independent way.  If the logging module is not configured,
    these logs will not be output anywhere.  See :ref:`logging_setup` for
    more information on how to set up and use the logging module with
    disnake.

Version Related Info
---------------------

There are two main ways to query version information about the library. For guarantees, check :ref:`version_guarantees`.

.. data:: version_info

    A named tuple that is similar to :obj:`py:sys.version_info`.

    Just like :obj:`py:sys.version_info` the valid values for ``releaselevel`` are
    'alpha', 'beta', 'candidate' and 'final'.

.. data:: __version__

    A string representation of the version. e.g. ``'1.0.0rc1'``. This is based
    off of :pep:`440`.

Clients
--------

Client
~~~~~~~

.. attributetable:: Client

.. autoclass:: Client
    :members:
    :exclude-members: fetch_guilds, event

    .. automethod:: Client.event()
        :decorator:

    .. automethod:: Client.fetch_guilds
        :async-for:

AutoShardedClient
~~~~~~~~~~~~~~~~~~

.. attributetable:: AutoShardedClient

.. autoclass:: AutoShardedClient
    :members:

Application Info
------------------

AppInfo
~~~~~~~~

.. attributetable:: AppInfo

.. autoclass:: AppInfo()
    :members:

PartialAppInfo
~~~~~~~~~~~~~~~

.. attributetable:: PartialAppInfo

.. autoclass:: PartialAppInfo()
    :members:

Team
~~~~~

.. attributetable:: Team

.. autoclass:: Team()
    :members:

TeamMember
~~~~~~~~~~~

.. attributetable:: TeamMember

.. autoclass:: TeamMember()
    :members:

InstallParams
~~~~~~~~~~~~~

.. attributetable:: InstallParams

.. autoclass:: InstallParams()
    :members:

Voice Related
---------------

VoiceClient
~~~~~~~~~~~~

.. attributetable:: VoiceClient

.. autoclass:: VoiceClient()
    :members:
    :exclude-members: connect, on_voice_state_update, on_voice_server_update

VoiceProtocol
~~~~~~~~~~~~~~~

.. attributetable:: VoiceProtocol

.. autoclass:: VoiceProtocol
    :members:

AudioSource
~~~~~~~~~~~~

.. attributetable:: AudioSource

.. autoclass:: AudioSource
    :members:

PCMAudio
~~~~~~~~~

.. attributetable:: PCMAudio

.. autoclass:: PCMAudio
    :members:

FFmpegAudio
~~~~~~~~~~~~

.. attributetable:: FFmpegAudio

.. autoclass:: FFmpegAudio
    :members:

FFmpegPCMAudio
~~~~~~~~~~~~~~~

.. attributetable:: FFmpegPCMAudio

.. autoclass:: FFmpegPCMAudio
    :members:

FFmpegOpusAudio
~~~~~~~~~~~~~~~~

.. attributetable:: FFmpegOpusAudio

.. autoclass:: FFmpegOpusAudio
    :members:

PCMVolumeTransformer
~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: PCMVolumeTransformer

.. autoclass:: PCMVolumeTransformer
    :members:

Opus Library
~~~~~~~~~~~~~

.. autofunction:: disnake.opus.load_opus

.. autofunction:: disnake.opus.is_loaded

.. _discord-api-events:

Event Reference
---------------

This section outlines the different types of events listened by :class:`Client`.

There are two ways to register an event, the first way is through the use of
:meth:`Client.event`. The second way is through subclassing :class:`Client` and
overriding the specific events. For example: ::

    import disnake

    class MyClient(disnake.Client):
        async def on_message(self, message):
            if message.author == self.user:
                return

            if message.content.startswith('$hello'):
                await message.channel.send('Hello World!')


If an event handler raises an exception, :func:`on_error` will be called
to handle it, which defaults to print a traceback and ignoring the exception.

.. warning::

    All the events must be a |coroutine_link|_. If they aren't, then you might get unexpected
    errors. In order to turn a function into a coroutine they must be ``async def``
    functions.

Client
~~~~~~

This section documents events related to :class:`Client` and its connectivity to Discord.

.. function:: on_connect()

    Called when the client has successfully connected to Discord. This is not
    the same as the client being fully prepared, see :func:`on_ready` for that.

    The warnings on :func:`on_ready` also apply.

.. function:: on_disconnect()

    Called when the client has disconnected from Discord, or a connection attempt to Discord has failed.
    This could happen either through the internet being disconnected, explicit calls to close,
    or Discord terminating the connection one way or the other.

    This function can be called many times without a corresponding :func:`on_connect` call.

.. function:: on_error(event, *args, **kwargs)

    Usually when an event raises an uncaught exception, a traceback is
    printed to stderr and the exception is ignored. If you want to
    change this behaviour and handle the exception for whatever reason
    yourself, this event can be overridden. Which, when done, will
    suppress the default action of printing the traceback.

    The information of the exception raised and the exception itself can
    be retrieved with a standard call to :func:`sys.exc_info`.

    If you want exception to propagate out of the :class:`Client` class
    you can define an ``on_error`` handler consisting of a single empty
    :ref:`raise statement <py:raise>`. Exceptions raised by ``on_error`` will not be
    handled in any way by :class:`Client`.

    .. note::

        ``on_error`` will only be dispatched to :meth:`Client.event`.

        It will not be received by :meth:`Client.wait_for`, or, if used,
        :ref:`ext_commands_api_bot` listeners such as
        :meth:`~ext.commands.Bot.listen` or :meth:`~ext.commands.Cog.listener`.

    :param event: The name of the event that raised the exception.
    :type event: :class:`str`

    :param args: The positional arguments for the event that raised the
        exception.
    :param kwargs: The keyword arguments for the event that raised the
        exception.

.. function:: on_gateway_error(event, data, shard_id, exc)

    When a (known) gateway event cannot be parsed, a traceback is printed to
    stderr and the exception is ignored by default. This should generally
    not happen and is usually either a library issue, or caused by a breaking API change.

    To change this behaviour, for example to completely stop the bot, this event can be overridden.

    This can also be disabled completely by passing ``enable_gateway_error_handler=False``
    to the client on initialization, restoring the pre-v2.6 behavior.

    .. versionadded:: 2.6

    .. note::
        ``on_gateway_error`` will only be dispatched to :meth:`Client.event`.

        It will not be received by :meth:`Client.wait_for`, or, if used,
        :ref:`ext_commands_api_bot` listeners such as
        :meth:`~ext.commands.Bot.listen` or :meth:`~ext.commands.Cog.listener`.

    .. note::
        This will not be dispatched for exceptions that occur while parsing ``READY`` and
        ``RESUMED`` event payloads, as exceptions in these events are considered fatal.

    :param event: The name of the gateway event that was the cause of the exception,
        for example ``MESSAGE_CREATE``.
    :type event: :class:`str`

    :param data: The raw event payload.
    :type data: :class:`Any`

    :param shard_id: The ID of the shard the exception occurred in, if applicable.
    :type shard_id: Optional[:class:`int`]

    :param exc: The exception that was raised.
    :type exc: :class:`Exception`

.. function:: on_ready()

    Called when the client is done preparing the data received from Discord. Usually after login is successful
    and the :attr:`Client.guilds` and co. are filled up.

    .. warning::

        This function is not guaranteed to be the first event called.
        Likewise, this function is **not** guaranteed to only be called
        once. This library implements reconnection logic and thus will
        end up calling this event whenever a RESUME request fails.

.. function:: on_resumed()

    Called when the client has resumed a session.

.. function:: on_shard_connect(shard_id)

    Similar to :func:`on_connect` except used by :class:`AutoShardedClient`
    to denote when a particular shard ID has connected to Discord.

    .. versionadded:: 1.4

    :param shard_id: The shard ID that has connected.
    :type shard_id: :class:`int`

.. function:: on_shard_disconnect(shard_id)

    Similar to :func:`on_disconnect` except used by :class:`AutoShardedClient`
    to denote when a particular shard ID has disconnected from Discord.

    .. versionadded:: 1.4

    :param shard_id: The shard ID that has disconnected.
    :type shard_id: :class:`int`

.. function:: on_shard_ready(shard_id)

    Similar to :func:`on_ready` except used by :class:`AutoShardedClient`
    to denote when a particular shard ID has become ready.

    :param shard_id: The shard ID that is ready.
    :type shard_id: :class:`int`

.. function:: on_shard_resumed(shard_id)

    Similar to :func:`on_resumed` except used by :class:`AutoShardedClient`
    to denote when a particular shard ID has resumed a session.

    .. versionadded:: 1.4

    :param shard_id: The shard ID that has resumed.
    :type shard_id: :class:`int`

.. function:: on_socket_event_type(event_type)

    Called whenever a websocket event is received from the WebSocket.

    This is mainly useful for logging how many events you are receiving
    from the Discord gateway.

    .. versionadded:: 2.0

    :param event_type: The event type from Discord that is received, e.g. ``'READY'``.
    :type event_type: :class:`str`

.. function:: on_socket_raw_receive(msg)

    Called whenever a message is completely received from the WebSocket, before
    it's processed and parsed. This event is always dispatched when a
    complete message is received and the passed data is not parsed in any way.

    This is only really useful for grabbing the WebSocket stream and
    debugging purposes.

    This requires setting the ``enable_debug_events`` setting in the :class:`Client`.

    .. note::

        This is only for the messages received from the client
        WebSocket. The voice WebSocket will not trigger this event.

    :param msg: The message passed in from the WebSocket library.
    :type msg: :class:`str`

.. function:: on_socket_raw_send(payload)

    Called whenever a send operation is done on the WebSocket before the
    message is sent. The passed parameter is the message that is being
    sent to the WebSocket.

    This is only really useful for grabbing the WebSocket stream and
    debugging purposes.

    This requires setting the ``enable_debug_events`` setting in the :class:`Client`.

    .. note::

        This is only for the messages sent from the client
        WebSocket. The voice WebSocket will not trigger this event.

    :param payload: The message that is about to be passed on to the
                    WebSocket library. It can be :class:`bytes` to denote a binary
                    message or :class:`str` to denote a regular text message.

Channels/Threads
~~~~~~~~~~~~~~~~

This section documents events related to Discord channels and threads.

.. function:: on_guild_channel_delete(channel)
              on_guild_channel_create(channel)

    Called whenever a guild channel is deleted or created.

    Note that you can get the guild from :attr:`~abc.GuildChannel.guild`.

    This requires :attr:`Intents.guilds` to be enabled.

    :param channel: The guild channel that got created or deleted.
    :type channel: :class:`abc.GuildChannel`

.. function:: on_guild_channel_update(before, after)

    Called whenever a guild channel is updated. e.g. changed name, topic, permissions.

    This requires :attr:`Intents.guilds` to be enabled.

    :param before: The updated guild channel's old info.
    :type before: :class:`abc.GuildChannel`
    :param after: The updated guild channel's new info.
    :type after: :class:`abc.GuildChannel`

.. function:: on_guild_channel_pins_update(channel, last_pin)

    Called whenever a message is pinned or unpinned from a guild channel.

    This requires :attr:`Intents.guilds` to be enabled.

    :param channel: The guild channel that had its pins updated.
    :type channel: Union[:class:`abc.GuildChannel`, :class:`Thread`]
    :param last_pin: The latest message that was pinned as an aware datetime in UTC. Could be ``None``.
    :type last_pin: Optional[:class:`datetime.datetime`]

.. function:: on_private_channel_update(before, after)

    Called whenever a private group DM is updated. e.g. changed name or topic.

    This requires :attr:`Intents.messages` to be enabled.

    :param before: The updated group channel's old info.
    :type before: :class:`GroupChannel`
    :param after: The updated group channel's new info.
    :type after: :class:`GroupChannel`

.. function:: on_private_channel_pins_update(channel, last_pin)

    Called whenever a message is pinned or unpinned from a private channel.

    :param channel: The private channel that had its pins updated.
    :type channel: :class:`abc.PrivateChannel`
    :param last_pin: The latest message that was pinned as an aware datetime in UTC. Could be ``None``.
    :type last_pin: Optional[:class:`datetime.datetime`]

.. function:: on_thread_create(thread)

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

    Called when a :class:`ThreadMember` leaves or joins a :class:`Thread`.

    You can get the thread a member belongs in by accessing :attr:`ThreadMember.thread`.

    On removal events, if the member being removed is not found in the internal cache,
    then this event will not be called. Consider using :func:`on_raw_thread_member_remove` instead.

    This requires :attr:`Intents.members` to be enabled.

    .. versionadded:: 2.0

    :param member: The member who joined or left.
    :type member: :class:`ThreadMember`

.. function:: on_thread_remove(thread)

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

    Called when a thread is deleted. If the thread is not found
    in the internal thread cache, then this event will not be called.
    Consider using :func:`on_raw_thread_delete` instead.

    Note that you can get the guild from :attr:`Thread.guild`.

    This requires :attr:`Intents.guilds` to be enabled.

    .. versionadded:: 2.0

    :param thread: The thread that got deleted.
    :type thread: :class:`Thread`

.. function:: on_raw_thread_member_remove(payload)

    Called when a :class:`ThreadMember` leaves :class:`Thread`.
    Unlike :func:`on_thread_member_remove`, this is called regardless of the thread member cache.

    You can get the thread a member belongs in by accessing :attr:`ThreadMember.thread`.

    This requires :attr:`Intents.members` to be enabled.

    .. versionadded:: 2.5

    :param payload: The raw event payload data.
    :type payload: :class:`RawThreadMemberRemoveEvent`

.. function:: on_raw_thread_update(after)

    Called whenever a thread is updated.
    Unlike :func:`on_thread_update`, this is called
    regardless of the state of the internal thread cache.

    This requires :attr:`Intents.guilds` to be enabled.

    .. versionadded:: 2.5

    :param thread: The updated thread.
    :type thread: :class:`Thread`

.. function:: on_raw_thread_delete(payload)

    Called whenever a thread is deleted.
    Unlike :func:`on_thread_delete`, this is called
    regardless of the state of the internal thread cache.

    Note that you can get the guild from :attr:`Thread.guild`.

    This requires :attr:`Intents.guilds` to be enabled.

    .. versionadded:: 2.5

    :param payload: The raw event payload data.
    :type payload: :class:`RawThreadDeleteEvent`

.. function:: on_webhooks_update(channel)

    Called whenever a webhook is created, modified, or removed from a guild channel.

    This requires :attr:`Intents.webhooks` to be enabled.

    :param channel: The channel that had its webhooks updated.
    :type channel: :class:`abc.GuildChannel`

Guilds
~~~~~~

This section documents events related to Discord guilds.

General
+++++++

.. function:: on_guild_join(guild)

    Called when a :class:`Guild` is either created by the :class:`Client` or when the
    :class:`Client` joins a guild.

    This requires :attr:`Intents.guilds` to be enabled.

    :param guild: The guild that was joined.
    :type guild: :class:`Guild`

.. function:: on_guild_remove(guild)

    Called when a :class:`Guild` is removed from the :class:`Client`.

    This happens through, but not limited to, these circumstances:

    - The client got banned.
    - The client got kicked.
    - The client left the guild.
    - The client or the guild owner deleted the guild.

    In order for this event to be invoked then the :class:`Client` must have
    been part of the guild to begin with. (i.e. it is part of :attr:`Client.guilds`)

    This requires :attr:`Intents.guilds` to be enabled.

    :param guild: The guild that got removed.
    :type guild: :class:`Guild`

.. function:: on_guild_update(before, after)

    Called when a :class:`Guild` updates, for example:

    - Changed name
    - Changed AFK channel
    - Changed AFK timeout
    - etc

    This requires :attr:`Intents.guilds` to be enabled.

    :param before: The guild prior to being updated.
    :type before: :class:`Guild`
    :param after: The guild after being updated.
    :type after: :class:`Guild`

.. function:: on_guild_available(guild)
              on_guild_unavailable(guild)

    Called when a guild becomes available or unavailable. The guild must have
    existed in the :attr:`Client.guilds` cache.

    This requires :attr:`Intents.guilds` to be enabled.

    :param guild: The :class:`Guild` that has changed availability.

Application Commands
++++++++++++++++++++

.. function:: on_application_command_permissions_update(permissions)

    Called when the permissions of an application command or
    the application-wide command permissions are updated.

    Note that this will also be called when permissions of other applications change,
    not just this application's permissions.

    .. versionadded:: 2.5

    :param permissions: The updated permission object.
    :type permissions: :class:`GuildApplicationCommandPermissions`

AutoMod
+++++++

.. function:: on_automod_action_execution(execution)

    Called when an auto moderation action is executed due to a rule triggering for a particular event.
    You must have the :attr:`~Permissions.manage_guild` permission to receive this.

    The guild this action has taken place in can be accessed using :attr:`AutoModActionExecution.guild`.

    This requires :attr:`Intents.automod_execution` to be enabled.

    In addition, :attr:`Intents.message_content` must be enabled to receive non-empty values
    for :attr:`AutoModActionExecution.content` and :attr:`AutoModActionExecution.matched_content`.

    .. note::
        This event will fire once per executed :class:`AutoModAction`, which means it
        will run multiple times when a rule is triggered, if that rule has multiple actions defined.

    .. versionadded:: 2.6

    :param execution: The auto moderation action execution data.
    :type execution: :class:`AutoModActionExecution`

.. function:: on_automod_rule_create(rule)

    Called when an :class:`AutoModRule` is created.
    You must have the :attr:`~Permissions.manage_guild` permission to receive this.

    This requires :attr:`Intents.automod_configuration` to be enabled.

    .. versionadded:: 2.6

    :param rule: The auto moderation rule that was created.
    :type rule: :class:`AutoModRule`

.. function:: on_automod_rule_update(rule)

    Called when an :class:`AutoModRule` is updated.
    You must have the :attr:`~Permissions.manage_guild` permission to receive this.

    This requires :attr:`Intents.automod_configuration` to be enabled.

    .. versionadded:: 2.6

    :param rule: The auto moderation rule that was updated.
    :type rule: :class:`AutoModRule`

.. function:: on_automod_rule_delete(rule)

    Called when an :class:`AutoModRule` is deleted.
    You must have the :attr:`~Permissions.manage_guild` permission to receive this.

    This requires :attr:`Intents.automod_configuration` to be enabled.

    .. versionadded:: 2.6

    :param rule: The auto moderation rule that was deleted.
    :type rule: :class:`AutoModRule`

Emojis
++++++

.. function:: on_guild_emojis_update(guild, before, after)

    Called when a :class:`Guild` adds or removes :class:`Emoji`.

    This requires :attr:`Intents.emojis_and_stickers` to be enabled.

    :param guild: The guild who got their emojis updated.
    :type guild: :class:`Guild`
    :param before: A list of emojis before the update.
    :type before: Sequence[:class:`Emoji`]
    :param after: A list of emojis after the update.
    :type after: Sequence[:class:`Emoji`]

Integrations
++++++++++++

.. function:: on_guild_integrations_update(guild)

    Called whenever an integration is created, modified, or removed from a guild.

    This requires :attr:`Intents.integrations` to be enabled.

    .. versionadded:: 1.4

    :param guild: The guild that had its integrations updated.
    :type guild: :class:`Guild`

.. function:: on_integration_create(integration)

    Called when an integration is created.

    This requires :attr:`Intents.integrations` to be enabled.

    .. versionadded:: 2.0

    :param integration: The integration that was created.
    :type integration: :class:`Integration`

.. function:: on_integration_update(integration)

    Called when an integration is updated.

    This requires :attr:`Intents.integrations` to be enabled.

    .. versionadded:: 2.0

    :param integration: The integration that was updated.
    :type integration: :class:`Integration`

.. function:: on_raw_integration_delete(payload)

    Called when an integration is deleted.

    This requires :attr:`Intents.integrations` to be enabled.

    .. versionadded:: 2.0

    :param payload: The raw event payload data.
    :type payload: :class:`RawIntegrationDeleteEvent`

Invites
+++++++

.. function:: on_invite_create(invite)

    Called when an :class:`Invite` is created.
    You must have the :attr:`~Permissions.manage_channels` permission to receive this.

    .. versionadded:: 1.3

    .. note::

        There is a rare possibility that the :attr:`Invite.guild` and :attr:`Invite.channel`
        attributes will be of :class:`Object` rather than the respective models.

    This requires :attr:`Intents.invites` to be enabled.

    :param invite: The invite that was created.
    :type invite: :class:`Invite`

.. function:: on_invite_delete(invite)

    Called when an :class:`Invite` is deleted.
    You must have the :attr:`~Permissions.manage_channels` permission to receive this.

    .. versionadded:: 1.3

    .. note::

        There is a rare possibility that the :attr:`Invite.guild` and :attr:`Invite.channel`
        attributes will be of :class:`Object` rather than the respective models.

        Outside of those two attributes, the only other attribute guaranteed to be
        filled by the Discord gateway for this event is :attr:`Invite.code`.

    This requires :attr:`Intents.invites` to be enabled.

    :param invite: The invite that was deleted.
    :type invite: :class:`Invite`

Members
+++++++

.. function:: on_member_join(member)
              on_member_remove(member)

    Called when a :class:`Member` leaves or joins a :class:`Guild`.
    If :func:`on_member_remove` is being used then consider using :func:`on_raw_member_remove` which will be called regardless of the cache.

    This requires :attr:`Intents.members` to be enabled.

    :param member: The member who joined or left.
    :type member: :class:`Member`

.. function:: on_member_update(before, after)

    Called when a :class:`Member` updates their profile.
    Consider using :func:`on_raw_member_update` which will be called regardless of the cache.

    This is called when one or more of the following things change, but is not limited to:

    - avatar (guild-specific)
    - current_timeout
    - nickname
    - pending
    - premium_since
    - roles

    This requires :attr:`Intents.members` to be enabled.

    :param before: The member's old info.
    :type before: :class:`Member`
    :param after: The member's updated info.
    :type after: :class:`Member`

.. function:: on_raw_member_remove(payload)

    Called when a member leaves a :class:`Guild`.
    Unlike :func:`on_member_remove`, this is called regardless of the member cache.

    .. versionadded:: 2.6

    :param payload: The raw event payload data.
    :type payload: :class:`RawGuildMemberRemoveEvent`

.. function:: on_raw_member_update(member)

    Called when a member updates their profile.
    Unlike :func:`on_member_update`, this is called regardless of the member cache.

    .. versionadded:: 2.6

    :param member: The member that was updated.
    :type member: :class:`Member`

.. function:: on_member_ban(guild, user)

    Called when user gets banned from a :class:`Guild`.

    This requires :attr:`Intents.bans` to be enabled.

    :param guild: The guild the user got banned from.
    :type guild: :class:`Guild`
    :param user: The user that got banned.
                 Can be either :class:`User` or :class:`Member` depending on
                 whether the user was in the guild at the time of removal.
    :type user: Union[:class:`User`, :class:`Member`]

.. function:: on_member_unban(guild, user)

    Called when a :class:`User` gets unbanned from a :class:`Guild`.

    This requires :attr:`Intents.bans` to be enabled.

    :param guild: The guild the user got unbanned from.
    :type guild: :class:`Guild`
    :param user: The user that got unbanned.
    :type user: :class:`User`

.. function:: on_presence_update(before, after)

    Called when a :class:`Member` updates their presence.

    This is called when one or more of the following things change:

    - status
    - activity

    This requires :attr:`Intents.presences` and :attr:`Intents.members` to be enabled.

    .. versionadded:: 2.0

    :param before: The updated member's old info.
    :type before: :class:`Member`
    :param after: The updated member's updated info.
    :type after: :class:`Member`

.. function:: on_user_update(before, after)

    Called when a :class:`User` is updated.

    This is called when one or more of the following things change, but is not limited to:

    - avatar
    - discriminator
    - name
    - public_flags

    This requires :attr:`Intents.members` to be enabled.

    :param before: The user's old info.
    :type before: :class:`User`
    :param after: The user's updated info.
    :type after: :class:`User`


Scheduled Events
++++++++++++++++

.. function:: on_guild_scheduled_event_create(event)
              on_guild_scheduled_event_delete(event)

    Called when a guild scheduled event is created or deleted.

    This requires :attr:`Intents.guild_scheduled_events` to be enabled.

    .. versionadded:: 2.3

    :param event: The guild scheduled event that was created or deleted.
    :type event: :class:`GuildScheduledEvent`

.. function:: on_guild_scheduled_event_update(before, after)

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

    Called when a user subscribes to or unsubscribes from a guild scheduled event.

    This requires :attr:`Intents.guild_scheduled_events` and :attr:`Intents.members` to be enabled.

    .. versionadded:: 2.3

    :param event: The guild scheduled event that the user subscribed to or unsubscribed from.
    :type event: :class:`GuildScheduledEvent`
    :param user: The user who subscribed to or unsubscribed from the event.
    :type user: Union[:class:`Member`, :class:`User`]

.. function:: on_raw_guild_scheduled_event_subscribe(payload)
              on_raw_guild_scheduled_event_unsubscribe(payload)

    Called when a user subscribes to or unsubscribes from a guild scheduled event.
    Unlike :func:`on_guild_scheduled_event_subscribe` and :func:`on_guild_scheduled_event_unsubscribe`,
    this is called regardless of the guild scheduled event cache.

    :param payload: The raw event payload data.
    :type payload: :class:`RawGuildScheduledEventUserActionEvent`

Stage Instances
+++++++++++++++

.. function:: on_stage_instance_create(stage_instance)
              on_stage_instance_delete(stage_instance)

    Called when a :class:`StageInstance` is created or deleted for a :class:`StageChannel`.

    .. versionadded:: 2.0

    :param stage_instance: The stage instance that was created or deleted.
    :type stage_instance: :class:`StageInstance`

.. function:: on_stage_instance_update(before, after)

    Called when a :class:`StageInstance` is updated.

    The following, but not limited to, examples illustrate when this event is called:

    - The topic is changed.
    - The privacy level is changed.

    .. versionadded:: 2.0

    :param before: The stage instance before the update.
    :type before: :class:`StageInstance`
    :param after: The stage instance after the update.
    :type after: :class:`StageInstance`

Stickers
++++++++

.. function:: on_guild_stickers_update(guild, before, after)

    Called when a :class:`Guild` updates its stickers.

    This requires :attr:`Intents.emojis_and_stickers` to be enabled.

    .. versionadded:: 2.0

    :param guild: The guild who got their stickers updated.
    :type guild: :class:`Guild`
    :param before: A list of stickers before the update.
    :type before: Sequence[:class:`GuildSticker`]
    :param after: A list of stickers after the update.
    :type after: Sequence[:class:`GuildSticker`]

Roles
+++++

.. function:: on_guild_role_create(role)
              on_guild_role_delete(role)

    Called when a :class:`Guild` creates or deletes a new :class:`Role`.

    To get the guild it belongs to, use :attr:`Role.guild`.

    This requires :attr:`Intents.guilds` to be enabled.

    :param role: The role that was created or deleted.
    :type role: :class:`Role`

.. function:: on_guild_role_update(before, after)

    Called when a :class:`Role` is changed guild-wide.

    This requires :attr:`Intents.guilds` to be enabled.

    :param before: The updated role's old info.
    :type before: :class:`Role`
    :param after: The updated role's updated info.
    :type after: :class:`Role`

Voice
+++++

.. function:: on_voice_state_update(member, before, after)

    Called when a :class:`Member` changes their :class:`VoiceState`.

    The following, but not limited to, examples illustrate when this event is called:

    - A member joins a voice or stage channel.
    - A member leaves a voice or stage channel.
    - A member is muted or deafened by their own accord.
    - A member is muted or deafened by a guild administrator.

    This requires :attr:`Intents.voice_states` to be enabled.

    :param member: The member whose voice states changed.
    :type member: :class:`Member`
    :param before: The voice state prior to the changes.
    :type before: :class:`VoiceState`
    :param after: The voice state after the changes.
    :type after: :class:`VoiceState`

.. _discord-api-utils:

Interactions
~~~~~~~~~~~~

This section documents events related to application commands and other interactions.

.. function:: on_application_command(interaction)

    Called when an application command is invoked.

    .. warning::

        This is a low level function that is not generally meant to be used.
        Consider using :class:`~ext.commands.Bot` or :class:`~ext.commands.InteractionBot` instead.

    .. warning::

        If you decide to override this event and are using :class:`~disnake.ext.commands.Bot` or related types,
        make sure to call :func:`Bot.process_application_commands <disnake.ext.commands.Bot.process_application_commands>`
        to ensure that the application commands are processed.

    .. versionadded:: 2.0

    :param interaction: The interaction object.
    :type interaction: :class:`ApplicationCommandInteraction`

.. function:: on_application_command_autocomplete(interaction)

    Called when an application command autocomplete is called.

    .. warning::

        This is a low level function that is not generally meant to be used.
        Consider using :class:`~ext.commands.Bot` or :class:`~ext.commands.InteractionBot` instead.

    .. warning::
        If you decide to override this event and are using :class:`~disnake.ext.commands.Bot` or related types,
        make sure to call :func:`Bot.process_app_command_autocompletion <disnake.ext.commands.Bot.process_app_command_autocompletion>`
        to ensure that the application command autocompletion is processed.

    .. versionadded:: 2.0

    :param interaction: The interaction object.
    :type interaction: :class:`ApplicationCommandInteraction`

.. function:: on_button_click(interaction)

    Called when a button is clicked.

    .. versionadded:: 2.0

    :param interaction: The interaction object.
    :type interaction: :class:`MessageInteraction`

.. function:: on_dropdown(interaction)

    Called when a select menu is clicked.

    .. versionadded:: 2.0

    :param interaction: The interaction object.
    :type interaction: :class:`MessageInteraction`

.. function:: on_interaction(interaction)

    Called when an interaction happened.

    This currently happens due to application command invocations or components being used.

    .. warning::

        This is a low level function that is not generally meant to be used.

    .. versionadded:: 2.0

    :param interaction: The interaction object.
    :type interaction: :class:`Interaction`

.. function:: on_message_interaction(interaction)

    Called when a message interaction happened.

    This currently happens due to components being used.

    .. versionadded:: 2.0

    :param interaction: The interaction object.
    :type interaction: :class:`MessageInteraction`

.. function:: on_modal_submit(interaction)

    Called when a modal is submitted.

    .. versionadded:: 2.4

    :param interaction: The interaction object.
    :type interaction: :class:`ModalInteraction`

Messages
~~~~~~~~

This section documents events related to Discord chat messages.

.. function:: on_message(message)

    Called when a :class:`Message` is created and sent.

    This requires :attr:`Intents.messages` to be enabled.

    .. warning::

        Your bot's own messages and private messages are sent through this
        event. This can lead cases of 'recursion' depending on how your bot was
        programmed. If you want the bot to not reply to itself, consider
        checking the user IDs. Note that :class:`~ext.commands.Bot` does not
        have this problem.

    .. note::

        Not all messages will have ``content``. This is a Discord limitation.
        See the docs of :attr:`Intents.message_content` for more information.

    :param message: The current message.
    :type message: :class:`Message`

.. function:: on_message_delete(message)

    Called when a message is deleted. If the message is not found in the
    internal message cache, then this event will not be called.
    Messages might not be in cache if the message is too old
    or the client is participating in high traffic guilds.

    If this occurs increase the :class:`max_messages <Client>` parameter
    or use the :func:`on_raw_message_delete` event instead.

    This requires :attr:`Intents.messages` to be enabled.

    .. note::

        Not all messages will have ``content``. This is a Discord limitation.
        See the docs of :attr:`Intents.message_content` for more information.


    :param message: The deleted message.
    :type message: :class:`Message`

.. function:: on_message_edit(before, after)

    Called when a :class:`Message` receives an update event. If the message is not found
    in the internal message cache, then these events will not be called.
    Messages might not be in cache if the message is too old
    or the client is participating in high traffic guilds.

    If this occurs increase the :class:`max_messages <Client>` parameter
    or use the :func:`on_raw_message_edit` event instead.

    .. note::

        Not all messages will have ``content``. This is a Discord limitation.
        See the docs of :attr:`Intents.message_content` for more information.

    The following non-exhaustive cases trigger this event:

    - A message has been pinned or unpinned.
    - The message content has been changed.
    - The message has received an embed.

        - For performance reasons, the embed server does not do this in a "consistent" manner.

    - The message's embeds were suppressed or unsuppressed.
    - A call message has received an update to its participants or ending time.

    This requires :attr:`Intents.messages` to be enabled.

    :param before: The previous version of the message.
    :type before: :class:`Message`
    :param after: The current version of the message.
    :type after: :class:`Message`

.. function:: on_bulk_message_delete(messages)

    Called when messages are bulk deleted. If none of the messages deleted
    are found in the internal message cache, then this event will not be called.
    If individual messages were not found in the internal message cache,
    this event will still be called, but the messages not found will not be included in
    the messages list. Messages might not be in cache if the message is too old
    or the client is participating in high traffic guilds.

    If this occurs increase the :class:`max_messages <Client>` parameter
    or use the :func:`on_raw_bulk_message_delete` event instead.

    This requires :attr:`Intents.messages` to be enabled.

    :param messages: The messages that have been deleted.
    :type messages: List[:class:`Message`]

.. function:: on_raw_message_delete(payload)

    Called when a message is deleted. Unlike :func:`on_message_delete`, this is
    called regardless of the message being in the internal message cache or not.

    If the message is found in the message cache,
    it can be accessed via :attr:`RawMessageDeleteEvent.cached_message`

    This requires :attr:`Intents.messages` to be enabled.

    :param payload: The raw event payload data.
    :type payload: :class:`RawMessageDeleteEvent`

.. function:: on_raw_message_edit(payload)

    Called when a message is edited. Unlike :func:`on_message_edit`, this is called
    regardless of the state of the internal message cache.

    If the message is found in the message cache,
    it can be accessed via :attr:`RawMessageUpdateEvent.cached_message`. The cached message represents
    the message before it has been edited. For example, if the content of a message is modified and
    triggers the :func:`on_raw_message_edit` coroutine, the :attr:`RawMessageUpdateEvent.cached_message`
    will return a :class:`Message` object that represents the message before the content was modified.

    Due to the inherently raw nature of this event, the data parameter coincides with
    the raw data given by the `gateway <https://discord.com/developers/docs/topics/gateway#message-update>`_.

    Since the data payload can be partial, care must be taken when accessing stuff in the dictionary.
    One example of a common case of partial data is when the ``'content'`` key is inaccessible. This
    denotes an "embed" only edit, which is an edit in which only the embeds are updated by the Discord
    embed server.

    This requires :attr:`Intents.messages` to be enabled.

    :param payload: The raw event payload data.
    :type payload: :class:`RawMessageUpdateEvent`

.. function:: on_raw_bulk_message_delete(payload)

    Called when a bulk delete is triggered. Unlike :func:`on_bulk_message_delete`, this is
    called regardless of the messages being in the internal message cache or not.

    If the messages are found in the message cache,
    they can be accessed via :attr:`RawBulkMessageDeleteEvent.cached_messages`

    This requires :attr:`Intents.messages` to be enabled.

    :param payload: The raw event payload data.
    :type payload: :class:`RawBulkMessageDeleteEvent`

.. function:: on_reaction_add(reaction, user)

    Called when a message has a reaction added to it. Similar to :func:`on_message_edit`,
    if the message is not found in the internal message cache, then this
    event will not be called. Consider using :func:`on_raw_reaction_add` instead.

    .. note::

        To get the :class:`Message` being reacted, access it via :attr:`Reaction.message`.

    This requires :attr:`Intents.reactions` to be enabled.

    .. note::

        This doesn't require :attr:`Intents.members` within a guild context,
        but due to Discord not providing updated user information in a direct message
        it's required for direct messages to receive this event.
        Consider using :func:`on_raw_reaction_add` if you need this and do not otherwise want
        to enable the members intent.

    :param reaction: The current state of the reaction.
    :type reaction: :class:`Reaction`
    :param user: The user who added the reaction.
    :type user: Union[:class:`Member`, :class:`User`]

.. function:: on_reaction_remove(reaction, user)

    Called when a message has a reaction removed from it. Similar to on_message_edit,
    if the message is not found in the internal message cache, then this event
    will not be called.

    .. note::

        To get the message being reacted, access it via :attr:`Reaction.message`.

    This requires both :attr:`Intents.reactions` and :attr:`Intents.members` to be enabled.

    .. note::

        Consider using :func:`on_raw_reaction_remove` if you need this and do not want
        to enable the members intent.

    :param reaction: The current state of the reaction.
    :type reaction: :class:`Reaction`
    :param user: The user who added the reaction.
    :type user: Union[:class:`Member`, :class:`User`]

.. function:: on_reaction_clear(message, reactions)

    Called when a message has all its reactions removed from it. Similar to :func:`on_message_edit`,
    if the message is not found in the internal message cache, then this event
    will not be called. Consider using :func:`on_raw_reaction_clear` instead.

    This requires :attr:`Intents.reactions` to be enabled.

    :param message: The message that had its reactions cleared.
    :type message: :class:`Message`
    :param reactions: The reactions that were removed.
    :type reactions: List[:class:`Reaction`]

.. function:: on_reaction_clear_emoji(reaction)

    Called when a message has a specific reaction removed from it. Similar to :func:`on_message_edit`,
    if the message is not found in the internal message cache, then this event
    will not be called. Consider using :func:`on_raw_reaction_clear_emoji` instead.

    This requires :attr:`Intents.reactions` to be enabled.

    .. versionadded:: 1.3

    :param reaction: The reaction that got cleared.
    :type reaction: :class:`Reaction`

.. function:: on_raw_reaction_add(payload)

    Called when a message has a reaction added. Unlike :func:`on_reaction_add`, this is
    called regardless of the state of the internal message cache.

    This requires :attr:`Intents.reactions` to be enabled.

    :param payload: The raw event payload data.
    :type payload: :class:`RawReactionActionEvent`

.. function:: on_raw_reaction_remove(payload)

    Called when a message has a reaction removed. Unlike :func:`on_reaction_remove`, this is
    called regardless of the state of the internal message cache.

    This requires :attr:`Intents.reactions` to be enabled.

    :param payload: The raw event payload data.
    :type payload: :class:`RawReactionActionEvent`

.. function:: on_raw_reaction_clear(payload)

    Called when a message has all its reactions removed. Unlike :func:`on_reaction_clear`,
    this is called regardless of the state of the internal message cache.

    This requires :attr:`Intents.reactions` to be enabled.

    :param payload: The raw event payload data.
    :type payload: :class:`RawReactionClearEvent`

.. function:: on_raw_reaction_clear_emoji(payload)

    Called when a message has a specific reaction removed from it. Unlike :func:`on_reaction_clear_emoji` this is called
    regardless of the state of the internal message cache.

    This requires :attr:`Intents.reactions` to be enabled.

    .. versionadded:: 1.3

    :param payload: The raw event payload data.
    :type payload: :class:`RawReactionClearEmojiEvent`

.. function:: on_typing(channel, user, when)

    Called when someone begins typing a message.

    The ``channel`` parameter can be a :class:`abc.Messageable` instance, or a :class:`ForumChannel`.
    If channel is an :class:`abc.Messageable` instance, it could be a :class:`TextChannel`, :class:`VoiceChannel`, :class:`GroupChannel`,
    or :class:`DMChannel`.

    .. versionchanged:: 2.5
        ``channel`` may be a type :class:`ForumChannel`

    If the ``channel`` is a :class:`TextChannel`, :class:`ForumChannel`, or :class:`VoiceChannel` then the
    ``user`` parameter is a :class:`Member`, otherwise it is a :class:`User`.

    If the ``channel`` is a :class:`DMChannel` and the user is not found in the internal user/member cache,
    then this event will not be called. Consider using :func:`on_raw_typing` instead.

    This requires :attr:`Intents.typing` and :attr:`Intents.guilds` to be enabled.

    .. note::

        This doesn't require :attr:`Intents.members` within a guild context,
        but due to Discord not providing updated user information in a direct message
        it's required for direct messages to receive this event, if the bot didn't explicitly
        open the DM channel in the same session (through :func:`User.create_dm`, :func:`Client.create_dm`,
        or indirectly by sending a message to the user).
        Consider using :func:`on_raw_typing` if you need this and do not otherwise want
        to enable the members intent.

    :param channel: The location where the typing originated from.
    :type channel: Union[:class:`abc.Messageable`, :class:`ForumChannel`]
    :param user: The user that started typing.
    :type user: Union[:class:`User`, :class:`Member`]
    :param when: When the typing started as an aware datetime in UTC.
    :type when: :class:`datetime.datetime`

.. function:: on_raw_typing(data)

    Called when someone begins typing a message.

    This is similar to :func:`on_typing` except that it is called regardless of
    whether :attr:`Intents.members` and :attr:`Intents.guilds` are enabled.

    :param data: The raw event payload data.
    :type data: :class:`RawTypingEvent`

Utility Functions
-----------------

.. autofunction:: disnake.utils.find

.. autofunction:: disnake.utils.get

.. autofunction:: disnake.utils.snowflake_time

.. autofunction:: disnake.utils.oauth_url

.. autofunction:: disnake.utils.remove_markdown

.. autofunction:: disnake.utils.escape_markdown

.. autofunction:: disnake.utils.escape_mentions

.. autofunction:: disnake.utils.resolve_invite

.. autofunction:: disnake.utils.resolve_template

.. autofunction:: disnake.utils.sleep_until

.. autofunction:: disnake.utils.utcnow

.. autofunction:: disnake.utils.format_dt

.. autofunction:: disnake.utils.as_chunks

.. autofunction:: disnake.utils.search_directory

.. autofunction:: disnake.utils.as_valid_locale

.. _discord-api-enums:

Enumerations
-------------

The API provides some enumerations for certain types of strings to avoid the API
from being stringly typed in case the strings change in the future.

All enumerations are subclasses of an internal class which mimics the behaviour
of :class:`enum.Enum`.

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

.. class:: MessageType

    Specifies the type of :class:`Message`. This is used to denote if a message
    is to be interpreted as a system message or a regular message.

    .. container:: operations

      .. describe:: x == y

          Checks if two messages are equal.
      .. describe:: x != y

          Checks if two messages are not equal.

    .. attribute:: default

        The default message type. This is the same as regular messages.
    .. attribute:: recipient_add

        The system message when a user is added to a group private
        message or a thread.
    .. attribute:: recipient_remove

        The system message when a user is removed from a group private
        message or a thread.
    .. attribute:: call

        The system message denoting call state, e.g. missed call, started call,
        etc.
    .. attribute:: channel_name_change

        The system message denoting that a channel's name has been changed.
    .. attribute:: channel_icon_change

        The system message denoting that a channel's icon has been changed.
    .. attribute:: pins_add

        The system message denoting that a pinned message has been added to a channel.
    .. attribute:: new_member

        The system message denoting that a new member has joined a Guild.

    .. attribute:: premium_guild_subscription

        The system message denoting that a member has "nitro boosted" a guild.
    .. attribute:: premium_guild_tier_1

        The system message denoting that a member has "nitro boosted" a guild
        and it achieved level 1.
    .. attribute:: premium_guild_tier_2

        The system message denoting that a member has "nitro boosted" a guild
        and it achieved level 2.
    .. attribute:: premium_guild_tier_3

        The system message denoting that a member has "nitro boosted" a guild
        and it achieved level 3.
    .. attribute:: channel_follow_add

        The system message denoting that an announcement channel has been followed.

        .. versionadded:: 1.3
    .. attribute:: guild_stream

        The system message denoting that a member is streaming in the guild.

        .. versionadded:: 1.7
    .. attribute:: guild_discovery_disqualified

        The system message denoting that the guild is no longer eligible for Server
        Discovery.

        .. versionadded:: 1.7
    .. attribute:: guild_discovery_requalified

        The system message denoting that the guild has become eligible again for Server
        Discovery.

        .. versionadded:: 1.7
    .. attribute:: guild_discovery_grace_period_initial_warning

        The system message denoting that the guild has failed to meet the Server
        Discovery requirements for one week.

        .. versionadded:: 1.7
    .. attribute:: guild_discovery_grace_period_final_warning

        The system message denoting that the guild has failed to meet the Server
        Discovery requirements for 3 weeks in a row.

        .. versionadded:: 1.7
    .. attribute:: thread_created

        The system message denoting that a thread has been created. This is only
        sent if the thread has been created from an older message. The period of time
        required for a message to be considered old cannot be relied upon and is up to
        Discord.

        .. versionadded:: 2.0
    .. attribute:: reply

        The system message denoting that the author is replying to a message.

        .. versionadded:: 2.0
    .. attribute:: application_command

        The system message denoting that an application (or "slash") command was executed.

        .. versionadded:: 2.0
    .. attribute:: guild_invite_reminder

        The system message sent as a reminder to invite people to the guild.

        .. versionadded:: 2.0
    .. attribute:: thread_starter_message

        The system message denoting the message in the thread that is the one that started the
        thread's conversation topic.

        .. versionadded:: 2.0
    .. attribute:: context_menu_command

        The system message denoting that a context menu command was executed.

        .. versionadded:: 2.3
    .. attribute:: auto_moderation_action

        The system message denoting that an auto moderation action was executed.

        .. versionadded:: 2.5

.. class:: UserFlags

    Represents Discord User flags.

    .. attribute:: staff

        The user is a Discord Employee.
    .. attribute:: partner

        The user is a Discord Partner.
    .. attribute:: hypesquad

        The user is a HypeSquad Events member.
    .. attribute:: bug_hunter

        The user is a Bug Hunter.
    .. attribute:: mfa_sms

        The user has SMS recovery for Multi Factor Authentication enabled.
    .. attribute:: premium_promo_dismissed

        The user has dismissed the Discord Nitro promotion.
    .. attribute:: hypesquad_bravery

        The user is a HypeSquad Bravery member.
    .. attribute:: hypesquad_brilliance

        The user is a HypeSquad Brilliance member.
    .. attribute:: hypesquad_balance

        The user is a HypeSquad Balance member.
    .. attribute:: early_supporter

        The user is an Early Supporter.
    .. attribute:: team_user

        The user is a Team User.
    .. attribute:: system

        The user is a system user (i.e. represents Discord officially).
    .. attribute:: has_unread_urgent_messages

        The user has an unread system message.
    .. attribute:: bug_hunter_level_2

        The user is a Bug Hunter Level 2.
    .. attribute:: verified_bot

        The user is a Verified Bot.
    .. attribute:: verified_bot_developer

        The user is an Early Verified Bot Developer.
    .. attribute:: discord_certified_moderator

        The user is a Discord Certified Moderator.
    .. attribute:: http_interactions_bot

        The user is a bot that only uses HTTP interactions.

        .. versionadded:: 2.3
    .. attribute:: spammer

        The user is marked as a spammer.

        .. versionadded:: 2.3

.. class:: ActivityType

    Specifies the type of :class:`Activity`. This is used to check how to
    interpret the activity itself.

    .. attribute:: unknown

        An unknown activity type. This should generally not happen.
    .. attribute:: playing

        A "Playing" activity type.
    .. attribute:: streaming

        A "Streaming" activity type.
    .. attribute:: listening

        A "Listening" activity type.
    .. attribute:: watching

        A "Watching" activity type.
    .. attribute:: custom

        A custom activity type.
    .. attribute:: competing

        A competing activity type.

        .. versionadded:: 1.5

.. class:: PartyType

    Represents the type of a voice channel activity/application.

    .. attribute:: poker

        The "Poker Night" activity.
    .. attribute:: betrayal

        The "Betrayal.io" activity.
    .. attribute:: fishing

        The "Fishington.io" activity.
    .. attribute:: chess

        The "Chess In The Park" activity.
    .. attribute:: letter_tile

        The "Letter Tile" activity.
    .. attribute:: word_snack

        The "Word Snacks" activity.
    .. attribute:: doodle_crew

        The "Doodle Crew" activity.
    .. attribute:: checkers

        The "Checkers In The Park" activity.

        .. versionadded:: 2.3
    .. attribute:: spellcast

        The "SpellCast" activity.

        .. versionadded:: 2.3
    .. attribute:: watch_together

        The "Watch Together" activity, a Youtube application.

        .. versionadded:: 2.3
    .. attribute:: sketch_heads

        The "Sketch Heads" activity.

        .. versionadded:: 2.4
    .. attribute:: ocho

        The "Ocho" activity.

        .. versionadded:: 2.4

.. class:: ApplicationCommandType

    Represents the type of an application command.

    .. versionadded:: 2.1

    .. attribute:: chat_input

        Represents a slash command.
    .. attribute:: user

        Represents a user command from the context menu.
    .. attribute:: message

        Represents a message command from the context menu.

.. class:: ApplicationCommandPermissionType

    Represents the type of a permission of an application command.

    .. versionadded:: 2.5

    .. attribute:: role

        Represents a permission that affects roles.
    .. attribute:: user

        Represents a permission that affects users.
    .. attribute:: channel

        Represents a permission that affects channels.

.. class:: InteractionType

    Specifies the type of :class:`Interaction`.

    .. versionadded:: 2.0

    .. attribute:: ping

        Represents Discord pinging to see if the interaction response server is alive.
    .. attribute:: application_command

        Represents an application command interaction.
    .. attribute:: component

        Represents a component based interaction, i.e. using the Discord Bot UI Kit.
    .. attribute:: application_command_autocomplete

        Represents an application command autocomplete interaction.
    .. attribute:: modal_submit

        Represents a modal submit interaction.

.. class:: InteractionResponseType

    Specifies the response type for the interaction.

    .. versionadded:: 2.0

    .. attribute:: pong

        Pongs the interaction when given a ping.

        See also :meth:`InteractionResponse.pong`
    .. attribute:: channel_message

        Respond to the interaction with a message.

        See also :meth:`InteractionResponse.send_message`
    .. attribute:: deferred_channel_message

        Responds to the interaction with a message at a later time.

        See also :meth:`InteractionResponse.defer`
    .. attribute:: deferred_message_update

        Acknowledges the component interaction with a promise that
        the message will update later (though there is no need to actually update the message).

        See also :meth:`InteractionResponse.defer`
    .. attribute:: message_update

        Responds to the interaction by editing the message.

        See also :meth:`InteractionResponse.edit_message`
    .. attribute:: application_command_autocomplete_result

        Responds to the autocomplete interaction with suggested choices.

        See also :meth:`InteractionResponse.autocomplete`
    .. attribute:: modal

        Responds to the interaction by displaying a modal.

        See also :meth:`InteractionResponse.send_modal`

.. class:: ComponentType

    Represents the component type of a component.

    .. versionadded:: 2.0

    .. attribute:: action_row

        Represents the group component which holds different components in a row.
    .. attribute:: button

        Represents a button component.
    .. attribute:: select

        Represents a select component.
    .. attribute:: text_input

        Represents a text input component.

.. class:: OptionType

    Represents the type of an option.

    .. versionadded:: 2.1

    .. attribute:: sub_command

        Represents a sub command of the main command or group.
    .. attribute:: sub_command_group

        Represents a sub command group of the main command.
    .. attribute:: string

        Represents a string option.
    .. attribute:: integer

        Represents an integer option.
    .. attribute:: boolean

        Represents a boolean option.
    .. attribute:: user

        Represents a user option.
    .. attribute:: channel

        Represents a channel option.
    .. attribute:: role

        Represents a role option.
    .. attribute:: mentionable

        Represents a role + user option.
    .. attribute:: number

        Represents a float option.
    .. attribute:: attachment

        Represents an attachment option.

        .. versionadded:: 2.4


.. class:: ButtonStyle

    Represents the style of the button component.

    .. versionadded:: 2.0

    .. attribute:: primary

        Represents a blurple button for the primary action.
    .. attribute:: secondary

        Represents a grey button for the secondary action.
    .. attribute:: success

        Represents a green button for a successful action.
    .. attribute:: danger

        Represents a red button for a dangerous action.
    .. attribute:: link

        Represents a link button.

    .. attribute:: blurple

        An alias for :attr:`primary`.
    .. attribute:: grey

        An alias for :attr:`secondary`.
    .. attribute:: gray

        An alias for :attr:`secondary`.
    .. attribute:: green

        An alias for :attr:`success`.
    .. attribute:: red

        An alias for :attr:`danger`.
    .. attribute:: url

        An alias for :attr:`link`.

.. class:: TextInputStyle

    Represents a style of the text input component.

    .. versionadded:: 2.4

    .. attribute:: short

        Represents a single-line text input component.
    .. attribute:: paragraph

        Represents a multi-line text input component.
    .. attribute:: single_line

        An alias for :attr:`short`.
    .. attribute:: multi_line

        An alias for :attr:`paragraph`.
    .. attribute:: long

        An alias for :attr:`paragraph`.


.. class:: VerificationLevel

    Specifies a :class:`Guild`\'s verification level, which is the criteria in
    which a member must meet before being able to send messages to the guild.

    .. container:: operations

        .. versionadded:: 2.0

        .. describe:: x == y

            Checks if two verification levels are equal.
        .. describe:: x != y

            Checks if two verification levels are not equal.
        .. describe:: x > y

            Checks if a verification level is higher than another.
        .. describe:: x < y

            Checks if a verification level is lower than another.
        .. describe:: x >= y

            Checks if a verification level is higher or equal to another.
        .. describe:: x <= y

            Checks if a verification level is lower or equal to another.

    .. attribute:: none

        No criteria set.
    .. attribute:: low

        Member must have a verified email on their Discord account.
    .. attribute:: medium

        Member must have a verified email and be registered on Discord for more
        than five minutes.
    .. attribute:: high

        Member must have a verified email, be registered on Discord for more
        than five minutes, and be a member of the guild itself for more than
        ten minutes.
    .. attribute:: highest

        Member must have a verified phone on their Discord account.

.. class:: NotificationLevel

    Specifies whether a :class:`Guild` has notifications on for all messages or mentions only by default.

    .. container:: operations

        .. versionadded:: 2.0

        .. describe:: x == y

            Checks if two notification levels are equal.
        .. describe:: x != y

            Checks if two notification levels are not equal.
        .. describe:: x > y

            Checks if a notification level is higher than another.
        .. describe:: x < y

            Checks if a notification level is lower than another.
        .. describe:: x >= y

            Checks if a notification level is higher or equal to another.
        .. describe:: x <= y

            Checks if a notification level is lower or equal to another.

    .. attribute:: all_messages

        Members receive notifications for every message regardless of them being mentioned.
    .. attribute:: only_mentions

        Members receive notifications for messages they are mentioned in.

.. class:: ContentFilter

    Specifies a :class:`Guild`\'s explicit content filter, which is the machine
    learning algorithms that Discord uses to detect if an image contains
    pornography or otherwise explicit content.

    .. container:: operations

        .. versionadded:: 2.0

        .. describe:: x == y

            Checks if two content filter levels are equal.
        .. describe:: x != y

            Checks if two content filter levels are not equal.
        .. describe:: x > y

            Checks if a content filter level is higher than another.
        .. describe:: x < y

            Checks if a content filter level is lower than another.
        .. describe:: x >= y

            Checks if a content filter level is higher or equal to another.
        .. describe:: x <= y

            Checks if a content filter level is lower or equal to another.

    .. attribute:: disabled

        The guild does not have the content filter enabled.
    .. attribute:: no_role

        The guild has the content filter enabled for members without a role.
    .. attribute:: all_members

        The guild has the content filter enabled for every member.

.. class:: Status

    Specifies a :class:`Member` 's status.

    .. attribute:: online

        The member is online.
    .. attribute:: offline

        The member is offline.
    .. attribute:: idle

        The member is idle.
    .. attribute:: dnd

        The member is "Do Not Disturb".
    .. attribute:: do_not_disturb

        An alias for :attr:`dnd`.
    .. attribute:: invisible

        The member is "invisible". In reality, this is only used in sending
        a presence a la :meth:`Client.change_presence`. When you receive a
        user's presence this will be :attr:`offline` instead.
    .. attribute:: streaming

        The member is live streaming to Twitch.

        .. versionadded:: 2.3


.. class:: AuditLogAction

    Represents the type of action being done for a :class:`AuditLogEntry`\,
    which is retrievable via :meth:`Guild.audit_logs`.

    .. attribute:: guild_update

        The guild has updated. Things that trigger this include:

        - Changing the guild vanity URL
        - Changing the guild invite splash
        - Changing the guild AFK channel or timeout
        - Changing the guild voice server region
        - Changing the guild icon, banner, or discovery splash
        - Changing the guild moderation settings
        - Changing things related to the guild widget

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Guild`.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.afk_channel`
        - :attr:`~AuditLogDiff.system_channel`
        - :attr:`~AuditLogDiff.afk_timeout`
        - :attr:`~AuditLogDiff.default_message_notifications`
        - :attr:`~AuditLogDiff.explicit_content_filter`
        - :attr:`~AuditLogDiff.mfa_level`
        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.owner`
        - :attr:`~AuditLogDiff.splash`
        - :attr:`~AuditLogDiff.discovery_splash`
        - :attr:`~AuditLogDiff.icon`
        - :attr:`~AuditLogDiff.banner`
        - :attr:`~AuditLogDiff.vanity_url_code`
        - :attr:`~AuditLogDiff.preferred_locale`
        - :attr:`~AuditLogDiff.description`
        - :attr:`~AuditLogDiff.rules_channel`
        - :attr:`~AuditLogDiff.public_updates_channel`
        - :attr:`~AuditLogDiff.widget_enabled`
        - :attr:`~AuditLogDiff.widget_channel`
        - :attr:`~AuditLogDiff.verification_level`
        - :attr:`~AuditLogDiff.premium_progress_bar_enabled`
        - :attr:`~AuditLogDiff.system_channel_flags`

    .. attribute:: channel_create

        A new channel was created.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        either a :class:`abc.GuildChannel` or :class:`Object` with an ID.

        A more filled out object in the :class:`Object` case can be found
        by using :attr:`~AuditLogEntry.after`.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.type`
        - :attr:`~AuditLogDiff.overwrites`
        - :attr:`~AuditLogDiff.topic`
        - :attr:`~AuditLogDiff.bitrate`
        - :attr:`~AuditLogDiff.rtc_region`
        - :attr:`~AuditLogDiff.video_quality_mode`
        - :attr:`~AuditLogDiff.default_auto_archive_duration`
        - :attr:`~AuditLogDiff.user_limit`
        - :attr:`~AuditLogDiff.slowmode_delay`
        - :attr:`~AuditLogDiff.nsfw`

    .. attribute:: channel_update

        A channel was updated. Things that trigger this include:

        - The channel name or topic was changed
        - The channel bitrate was changed

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`abc.GuildChannel` or :class:`Object` with an ID.

        A more filled out object in the :class:`Object` case can be found
        by using :attr:`~AuditLogEntry.after` or :attr:`~AuditLogEntry.before`.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.type`
        - :attr:`~AuditLogDiff.position`
        - :attr:`~AuditLogDiff.overwrites`
        - :attr:`~AuditLogDiff.topic`
        - :attr:`~AuditLogDiff.bitrate`
        - :attr:`~AuditLogDiff.rtc_region`
        - :attr:`~AuditLogDiff.video_quality_mode`
        - :attr:`~AuditLogDiff.default_auto_archive_duration`
        - :attr:`~AuditLogDiff.user_limit`
        - :attr:`~AuditLogDiff.slowmode_delay`
        - :attr:`~AuditLogDiff.nsfw`

    .. attribute:: channel_delete

        A channel was deleted.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        an :class:`Object` with an ID.

        A more filled out object can be found by using the
        :attr:`~AuditLogEntry.before` object.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.type`
        - :attr:`~AuditLogDiff.overwrites`
        - :attr:`~AuditLogDiff.topic`
        - :attr:`~AuditLogDiff.bitrate`
        - :attr:`~AuditLogDiff.rtc_region`
        - :attr:`~AuditLogDiff.video_quality_mode`
        - :attr:`~AuditLogDiff.default_auto_archive_duration`
        - :attr:`~AuditLogDiff.user_limit`
        - :attr:`~AuditLogDiff.slowmode_delay`
        - :attr:`~AuditLogDiff.nsfw`

    .. attribute:: overwrite_create

        A channel permission overwrite was created.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`abc.GuildChannel` or :class:`Object` with an ID.

        When this is the action, the type of :attr:`~AuditLogEntry.extra` is
        either a :class:`Role` or :class:`Member`. If the object is not found
        then it is a :class:`Object` with an ID being filled, a name, and a
        ``type`` attribute set to either ``'role'`` or ``'member'`` to help
        dictate what type of ID it is.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.deny`
        - :attr:`~AuditLogDiff.allow`
        - :attr:`~AuditLogDiff.id`
        - :attr:`~AuditLogDiff.type`

        .. versionchanged:: 2.6
            :attr:`~AuditLogDiff.type` for this action is now an :class:`int`.

    .. attribute:: overwrite_update

        A channel permission overwrite was changed, this is typically
        when the permission values change.

        See :attr:`overwrite_create` for more information on how the
        :attr:`~AuditLogEntry.target` and :attr:`~AuditLogEntry.extra` fields
        are set.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.deny`
        - :attr:`~AuditLogDiff.allow`
        - :attr:`~AuditLogDiff.id`
        - :attr:`~AuditLogDiff.type`

        .. versionchanged:: 2.6
            :attr:`~AuditLogDiff.type` for this action is now an :class:`int`.

    .. attribute:: overwrite_delete

        A channel permission overwrite was deleted.

        See :attr:`overwrite_create` for more information on how the
        :attr:`~AuditLogEntry.target` and :attr:`~AuditLogEntry.extra` fields
        are set.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.deny`
        - :attr:`~AuditLogDiff.allow`
        - :attr:`~AuditLogDiff.id`
        - :attr:`~AuditLogDiff.type`

        .. versionchanged:: 2.6
            :attr:`~AuditLogDiff.type` for this action is now an :class:`int`.

    .. attribute:: kick

        A member was kicked.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`User` who got kicked.

        When this is the action, :attr:`~AuditLogEntry.changes` is empty.

    .. attribute:: member_prune

        A member prune was triggered.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        set to ``None``.

        When this is the action, the type of :attr:`~AuditLogEntry.extra` is
        set to an unspecified proxy object with two attributes:

        - ``delete_members_days``: An integer specifying how far the prune was.
        - ``members_removed``: An integer specifying how many members were removed.

        When this is the action, :attr:`~AuditLogEntry.changes` is empty.

    .. attribute:: ban

        A member was banned.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`User` who got banned.

        When this is the action, :attr:`~AuditLogEntry.changes` is empty.

    .. attribute:: unban

        A member was unbanned.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`User` who got unbanned.

        When this is the action, :attr:`~AuditLogEntry.changes` is empty.

    .. attribute:: member_update

        A member has updated. This triggers in the following situations:

        - A nickname was changed
        - They were server muted or deafened (or it was undone)
        - They were timed out

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Member` or :class:`User` who got updated.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.nick`
        - :attr:`~AuditLogDiff.mute`
        - :attr:`~AuditLogDiff.deaf`
        - :attr:`~AuditLogDiff.timeout`

    .. attribute:: member_role_update

        A member's role has been updated. This triggers when a member
        either gains a role or loses a role.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Member` or :class:`User` who got the role.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.roles`

    .. attribute:: member_move

        A member's voice channel has been updated. This triggers when a
        member is moved to a different voice channel.

        When this is the action, the type of :attr:`~AuditLogEntry.extra` is
        set to an unspecified proxy object with two attributes:

        - ``channel``: A :class:`TextChannel` or :class:`Object` with the channel ID where the members were moved.
        - ``count``: An integer specifying how many members were moved.

        .. versionadded:: 1.3

    .. attribute:: member_disconnect

        A member's voice state has changed. This triggers when a
        member is force disconnected from voice.

        When this is the action, the type of :attr:`~AuditLogEntry.extra` is
        set to an unspecified proxy object with one attribute:

        - ``count``: An integer specifying how many members were disconnected.

        .. versionadded:: 1.3

    .. attribute:: bot_add

        A bot was added to the guild.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Member` or :class:`User` which was added to the guild.

        .. versionadded:: 1.3

    .. attribute:: role_create

        A new role was created.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Role` or a :class:`Object` with the ID.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.colour`
        - :attr:`~AuditLogDiff.mentionable`
        - :attr:`~AuditLogDiff.hoist`
        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.permissions`
        - :attr:`~AuditLogDiff.icon`
        - :attr:`~AuditLogDiff.emoji`

    .. attribute:: role_update

        A role was updated. This triggers in the following situations:

        - The name has changed
        - The permissions have changed
        - The colour has changed
        - Its hoist/mentionable state has changed

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Role` or a :class:`Object` with the ID.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.colour`
        - :attr:`~AuditLogDiff.mentionable`
        - :attr:`~AuditLogDiff.hoist`
        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.permissions`
        - :attr:`~AuditLogDiff.icon`
        - :attr:`~AuditLogDiff.emoji`

    .. attribute:: role_delete

        A role was deleted.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Object` with the ID.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.colour`
        - :attr:`~AuditLogDiff.mentionable`
        - :attr:`~AuditLogDiff.hoist`
        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.permissions`
        - :attr:`~AuditLogDiff.icon`
        - :attr:`~AuditLogDiff.emoji`

    .. attribute:: invite_create

        An invite was created.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Invite` that was created.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.max_age`
        - :attr:`~AuditLogDiff.code`
        - :attr:`~AuditLogDiff.temporary`
        - :attr:`~AuditLogDiff.inviter`
        - :attr:`~AuditLogDiff.channel`
        - :attr:`~AuditLogDiff.uses`
        - :attr:`~AuditLogDiff.max_uses`

    .. attribute:: invite_update

        An invite was updated.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Invite` that was updated.

    .. attribute:: invite_delete

        An invite was deleted.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Invite` that was deleted.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.max_age`
        - :attr:`~AuditLogDiff.code`
        - :attr:`~AuditLogDiff.temporary`
        - :attr:`~AuditLogDiff.inviter`
        - :attr:`~AuditLogDiff.channel`
        - :attr:`~AuditLogDiff.uses`
        - :attr:`~AuditLogDiff.max_uses`

    .. attribute:: webhook_create

        A webhook was created.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Webhook` or :class:`Object` with the webhook ID.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.channel`
        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.type`
        - :attr:`~AuditLogDiff.application_id`
        - :attr:`~AuditLogDiff.avatar`

        .. versionchanged:: 2.6
            Added :attr:`~AuditLogDiff.application_id`.

        .. versionchanged:: 2.6
            :attr:`~AuditLogDiff.type` for this action is now a :class:`WebhookType`.

        .. versionchanged:: 2.6
            Added support for :class:`Webhook` instead of plain :class:`Object`\s.

    .. attribute:: webhook_update

        A webhook was updated. This trigger in the following situations:

        - The webhook name changed
        - The webhook channel changed

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Webhook` or :class:`Object` with the webhook ID.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.channel`
        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.avatar`

        .. versionchanged:: 2.6
            Added support for :class:`Webhook` instead of plain :class:`Object`\s.

    .. attribute:: webhook_delete

        A webhook was deleted.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Object` with the webhook ID.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.channel`
        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.type`
        - :attr:`~AuditLogDiff.application_id`
        - :attr:`~AuditLogDiff.avatar`

        .. versionchanged:: 2.6
            Added :attr:`~AuditLogDiff.application_id`.

        .. versionchanged:: 2.6
            :attr:`~AuditLogDiff.type` for this action is now a :class:`WebhookType`.

    .. attribute:: emoji_create

        An emoji was created.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Emoji` or :class:`Object` with the emoji ID.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`

    .. attribute:: emoji_update

        An emoji was updated. This triggers when the name has changed.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Emoji` or :class:`Object` with the emoji ID.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`

    .. attribute:: emoji_delete

        An emoji was deleted.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Object` with the emoji ID.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`

    .. attribute:: message_delete

        A message was deleted by a moderator. Note that this
        only triggers if the message was deleted by someone other than the author.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Member` or :class:`User` who had their message deleted.

        When this is the action, the type of :attr:`~AuditLogEntry.extra` is
        set to an unspecified proxy object with two attributes:

        - ``count``: An integer specifying how many messages were deleted.
        - ``channel``: A :class:`TextChannel` or :class:`Object` with the channel ID where the message got deleted.

    .. attribute:: message_bulk_delete

        Messages were bulk deleted by a moderator.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`TextChannel` or :class:`Object` with the ID of the channel that was purged.

        When this is the action, the type of :attr:`~AuditLogEntry.extra` is
        set to an unspecified proxy object with one attribute:

        - ``count``: An integer specifying how many messages were deleted.

        .. versionadded:: 1.3

    .. attribute:: message_pin

        A message was pinned in a channel.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Member` or :class:`User` who had their message pinned.

        When this is the action, the type of :attr:`~AuditLogEntry.extra` is
        set to an unspecified proxy object with two attributes:

        - ``channel``: A :class:`TextChannel` or :class:`Object` with the channel ID where the message was pinned.
        - ``message_id``: the ID of the message which was pinned.

        .. versionadded:: 1.3

    .. attribute:: message_unpin

        A message was unpinned in a channel.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Member` or :class:`User` who had their message unpinned.

        When this is the action, the type of :attr:`~AuditLogEntry.extra` is
        set to an unspecified proxy object with two attributes:

        - ``channel``: A :class:`TextChannel` or :class:`Object` with the channel ID where the message was unpinned.
        - ``message_id``: the ID of the message which was unpinned.

        .. versionadded:: 1.3

    .. attribute:: integration_create

        A guild integration was created.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`PartialIntegration` or :class:`Object` with the integration ID
        of the integration which was created.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.type`

        .. versionadded:: 1.3

        .. versionchanged:: 2.6
            Added support for :class:`PartialIntegration` instead of plain :class:`Object`\s.

    .. attribute:: integration_update

        A guild integration was updated.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`PartialIntegration` or :class:`Object` with the integration ID
        of the integration which was updated.

        .. versionadded:: 1.3

        .. versionchanged:: 2.6
            Added support for :class:`PartialIntegration` instead of plain :class:`Object`\s.

    .. attribute:: integration_delete

        A guild integration was deleted.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Object` with the integration ID of the integration which was deleted.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.type`

        .. versionadded:: 1.3

    .. attribute:: guild_scheduled_event_create

        A guild scheduled event was created.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`GuildScheduledEvent` or :class:`Object` with the ID of the event
        which was created.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.description`
        - :attr:`~AuditLogDiff.privacy_level`
        - :attr:`~AuditLogDiff.status`
        - :attr:`~AuditLogDiff.entity_type`
        - :attr:`~AuditLogDiff.channel`
        - :attr:`~AuditLogDiff.location`
        - :attr:`~AuditLogDiff.image`

        .. versionadded:: 2.3

    .. attribute:: guild_scheduled_event_update

        A guild scheduled event was updated.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`GuildScheduledEvent` or :class:`Object` with the ID of the event
        which was updated.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.description`
        - :attr:`~AuditLogDiff.privacy_level`
        - :attr:`~AuditLogDiff.status`
        - :attr:`~AuditLogDiff.entity_type`
        - :attr:`~AuditLogDiff.channel`
        - :attr:`~AuditLogDiff.location`
        - :attr:`~AuditLogDiff.image`

        .. versionadded:: 2.3

    .. attribute:: guild_scheduled_event_delete

        A guild scheduled event was deleted.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Object` with the ID of the event which was deleted.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.description`
        - :attr:`~AuditLogDiff.privacy_level`
        - :attr:`~AuditLogDiff.status`
        - :attr:`~AuditLogDiff.entity_type`
        - :attr:`~AuditLogDiff.channel`
        - :attr:`~AuditLogDiff.location`
        - :attr:`~AuditLogDiff.image`

        .. versionadded:: 2.3

    .. attribute:: stage_instance_create

        A stage instance was started.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`StageInstance` or :class:`Object` with the ID of the stage
        instance which was created.

        When this is the action, the type of :attr:`~AuditLogEntry.extra` is
        set to an unspecified proxy object with one attribute:

        - ``channel``: The :class:`StageChannel` or :class:`Object` with the channel ID where the stage instance was started.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.topic`
        - :attr:`~AuditLogDiff.privacy_level`

        .. versionadded:: 2.0

    .. attribute:: stage_instance_update

        A stage instance was updated.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`StageInstance` or :class:`Object` with the ID of the stage
        instance which was updated.

        See :attr:`stage_instance_create` for more information on how the
        :attr:`~AuditLogEntry.extra` field is set.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.topic`
        - :attr:`~AuditLogDiff.privacy_level`

        .. versionadded:: 2.0

    .. attribute:: stage_instance_delete

        A stage instance was ended.

        See :attr:`stage_instance_create` for more information on how the
        :attr:`~AuditLogEntry.extra` field is set.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.topic`
        - :attr:`~AuditLogDiff.privacy_level`

        .. versionadded:: 2.0

    .. attribute:: sticker_create

        A sticker was created.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`GuildSticker` or :class:`Object` with the ID of the sticker
        which was created.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.emoji`
        - :attr:`~AuditLogDiff.type`
        - :attr:`~AuditLogDiff.format_type`
        - :attr:`~AuditLogDiff.description`
        - :attr:`~AuditLogDiff.available`

        .. versionadded:: 2.0

    .. attribute:: sticker_update

        A sticker was updated.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`GuildSticker` or :class:`Object` with the ID of the sticker
        which was updated.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.emoji`
        - :attr:`~AuditLogDiff.description`

        .. versionadded:: 2.0

    .. attribute:: sticker_delete

        A sticker was deleted.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Object` with the ID of the sticker which was deleted.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.emoji`
        - :attr:`~AuditLogDiff.type`
        - :attr:`~AuditLogDiff.format_type`
        - :attr:`~AuditLogDiff.description`
        - :attr:`~AuditLogDiff.available`

        .. versionadded:: 2.0

    .. attribute:: thread_create

        A thread was created.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Thread` or :class:`Object` with the ID of the thread which
        was created.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.archived`
        - :attr:`~AuditLogDiff.locked`
        - :attr:`~AuditLogDiff.auto_archive_duration`
        - :attr:`~AuditLogDiff.type`
        - :attr:`~AuditLogDiff.slowmode_delay`
        - :attr:`~AuditLogDiff.invitable`
        - :attr:`~AuditLogDiff.flags`

        .. versionadded:: 2.0

    .. attribute:: thread_update

        A thread was updated.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Thread` or :class:`Object` with the ID of the thread which
        was updated.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.archived`
        - :attr:`~AuditLogDiff.locked`
        - :attr:`~AuditLogDiff.auto_archive_duration`
        - :attr:`~AuditLogDiff.slowmode_delay`
        - :attr:`~AuditLogDiff.invitable`
        - :attr:`~AuditLogDiff.flags`

        .. versionadded:: 2.0

    .. attribute:: thread_delete

        A thread was deleted.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Object` with the ID of the thread which was deleted.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.archived`
        - :attr:`~AuditLogDiff.locked`
        - :attr:`~AuditLogDiff.auto_archive_duration`
        - :attr:`~AuditLogDiff.type`
        - :attr:`~AuditLogDiff.slowmode_delay`
        - :attr:`~AuditLogDiff.invitable`
        - :attr:`~AuditLogDiff.flags`

        .. versionadded:: 2.0

    .. attribute:: application_command_permission_update

        The permissions of an application command were updated.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`ApplicationCommand`, :class:`PartialIntegration`, or :class:`Object`
        with the ID of the command whose permissions were updated or the application ID
        if these are application-wide permissions.

        When this is the action, the type of :attr:`~AuditLogEntry.extra` is
        set to an unspecified proxy object with one attribute:

        - ``integration``: The :class:`PartialIntegration` or :class:`Object` with the application ID of the associated application.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.command_permissions`

        .. versionadded:: 2.5

        .. versionchanged:: 2.6
            Added support for :class:`PartialIntegration`, and added ``integration`` to :attr:`~AuditLogEntry.extra`.

    .. attribute:: automod_rule_create

        An auto moderation rule was created.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`AutoModRule` or :class:`Object` with the ID of the auto moderation rule which
        was created.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.enabled`
        - :attr:`~AuditLogDiff.trigger_type`
        - :attr:`~AuditLogDiff.event_type`
        - :attr:`~AuditLogDiff.actions`
        - :attr:`~AuditLogDiff.trigger_metadata`
        - :attr:`~AuditLogDiff.exempt_roles`
        - :attr:`~AuditLogDiff.exempt_channels`

        .. versionadded:: 2.6

    .. attribute:: automod_rule_update

        An auto moderation rule was updated.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`AutoModRule` or :class:`Object` with the ID of the auto moderation rule which
        was updated.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.enabled`
        - :attr:`~AuditLogDiff.trigger_type`
        - :attr:`~AuditLogDiff.event_type`
        - :attr:`~AuditLogDiff.actions`
        - :attr:`~AuditLogDiff.trigger_metadata`
        - :attr:`~AuditLogDiff.exempt_roles`
        - :attr:`~AuditLogDiff.exempt_channels`

        .. versionadded:: 2.6

    .. attribute:: automod_rule_delete

        An auto moderation rule was deleted.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Object` with the ID of the auto moderation rule which
        was deleted.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.enabled`
        - :attr:`~AuditLogDiff.trigger_type`
        - :attr:`~AuditLogDiff.event_type`
        - :attr:`~AuditLogDiff.actions`
        - :attr:`~AuditLogDiff.trigger_metadata`
        - :attr:`~AuditLogDiff.exempt_roles`
        - :attr:`~AuditLogDiff.exempt_channels`

        .. versionadded:: 2.6

    .. attribute:: automod_block_message

        A message was blocked by an auto moderation rule.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Member` or :class:`User` who had their message blocked.

        When this is the action, the type of :attr:`~AuditLogEntry.extra` is
        set to an unspecified proxy object with these attributes:

        - ``channel``: A :class:`~abc.GuildChannel`, :class:`Thread` or :class:`Object` with the channel ID where the message got blocked.
        - ``rule_name``: A :class:`str` with the name of the rule that matched.
        - ``rule_trigger_type``: An :class:`AutoModTriggerType` value with the trigger type of the rule.

    .. attribute:: automod_send_alert_message

        An alert message was sent by an auto moderation rule.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Member` or :class:`User` who had their message flagged.

        See :attr:`automod_block_message` for more information on how the
        :attr:`~AuditLogEntry.extra` field is set.

    .. attribute:: automod_timeout

        A user was timed out by an auto moderation rule.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Member` or :class:`User` who was timed out.

        See :attr:`automod_block_message` for more information on how the
        :attr:`~AuditLogEntry.extra` field is set.

.. class:: AuditLogActionCategory

    Represents the category that the :class:`AuditLogAction` belongs to.

    This can be retrieved via :attr:`AuditLogEntry.category`.

    .. attribute:: create

        The action is the creation of something.

    .. attribute:: delete

        The action is the deletion of something.

    .. attribute:: update

        The action is the update of something.

.. class:: TeamMembershipState

    Represents the membership state of a team member retrieved through :func:`Client.application_info`.

    .. versionadded:: 1.3

    .. attribute:: invited

        Represents an invited member.

    .. attribute:: accepted

        Represents a member currently in the team.

.. class:: WebhookType

    Represents the type of webhook that can be received.

    .. versionadded:: 1.3

    .. attribute:: incoming

        Represents a webhook that can post messages to channels with a token.

    .. attribute:: channel_follower

        Represents a webhook that is internally managed by Discord, used for following channels.

    .. attribute:: application

        Represents a webhook that is used for interactions or applications.

        .. versionadded:: 2.0

.. class:: ExpireBehaviour

    Represents the behaviour the :class:`Integration` should perform
    when a user's subscription has finished.

    There is an alias for this called ``ExpireBehavior``.

    .. versionadded:: 1.4

    .. attribute:: remove_role

        This will remove the :attr:`StreamIntegration.role` from the user
        when their subscription is finished.

    .. attribute:: kick

        This will kick the user when their subscription is finished.

.. class:: DefaultAvatar

    Represents the default avatar of a Discord :class:`User`

    .. attribute:: blurple

        Represents the default avatar with the color blurple.
        See also :attr:`Colour.blurple`
    .. attribute:: grey

        Represents the default avatar with the color grey.
        See also :attr:`Colour.greyple`
    .. attribute:: gray

        An alias for :attr:`grey`.
    .. attribute:: green

        Represents the default avatar with the color green.
        See also :attr:`Colour.green`
    .. attribute:: orange

        Represents the default avatar with the color orange.
        See also :attr:`Colour.orange`
    .. attribute:: red

        Represents the default avatar with the color red.
        See also :attr:`Colour.red`

.. class:: StickerType

    Represents the type of sticker.

    .. versionadded:: 2.0

    .. attribute:: standard

        Represents a standard sticker that all Nitro users can use.

    .. attribute:: guild

        Represents a custom sticker created in a guild.

.. class:: StickerFormatType

    Represents the type of sticker images.

    .. versionadded:: 1.6

    .. attribute:: png

        Represents a sticker with a png image.

    .. attribute:: apng

        Represents a sticker with an apng image.

    .. attribute:: lottie

        Represents a sticker with a lottie image.

.. class:: InviteTarget

    Represents the invite type for voice channel invites.

    .. versionadded:: 2.0

    .. attribute:: unknown

        The invite doesn't target anyone or anything.

    .. attribute:: stream

        A stream invite that targets a user.

    .. attribute:: embedded_application

        A stream invite that targets an embedded application.

.. class:: VideoQualityMode

    Represents the camera video quality mode for voice channel participants.

    .. versionadded:: 2.0

    .. attribute:: auto

        Represents auto camera video quality.

    .. attribute:: full

        Represents full camera video quality.

.. class:: StagePrivacyLevel

    Represents a stage instance's privacy level.

    .. versionadded:: 2.0

    .. attribute:: public

        The stage instance can be joined by external users.

        .. deprecated:: 2.5

            Public stages are no longer supported by discord.

    .. attribute:: closed

        The stage instance can only be joined by members of the guild.

    .. attribute:: guild_only

        Alias for :attr:`.closed`

.. class:: NSFWLevel

    Represents the NSFW level of a guild.

    .. versionadded:: 2.0

    .. container:: operations

        .. describe:: x == y

            Checks if two NSFW levels are equal.
        .. describe:: x != y

            Checks if two NSFW levels are not equal.
        .. describe:: x > y

            Checks if a NSFW level is higher than another.
        .. describe:: x < y

            Checks if a NSFW level is lower than another.
        .. describe:: x >= y

            Checks if a NSFW level is higher or equal to another.
        .. describe:: x <= y

            Checks if a NSFW level is lower or equal to another.

    .. attribute:: default

        The guild has not been categorised yet.

    .. attribute:: explicit

        The guild contains NSFW content.

    .. attribute:: safe

        The guild does not contain any NSFW content.

    .. attribute:: age_restricted

        The guild may contain NSFW content.

.. class:: GuildScheduledEventEntityType

    Represents the type of a guild scheduled event entity.

    .. versionadded:: 2.3

    .. attribute:: stage_instance

        The guild scheduled event will take place in a stage channel.

    .. attribute:: voice

        The guild scheduled event will take place in a voice channel.

    .. attribute:: external

        The guild scheduled event will take place in a custom location.

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

.. class:: GuildScheduledEventPrivacyLevel

    Represents the privacy level of a guild scheduled event.

    .. versionadded:: 2.3

    .. attribute:: guild_only

        The guild scheduled event is only for a specific guild.

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

.. class:: WidgetStyle

    Represents the supported widget image styles.

    .. versionadded:: 2.5

    .. attribute:: shield

        A shield style image with a Discord icon and the online member count.

    .. attribute:: banner1

        A large image with guild icon, name and online member count and a footer.

    .. attribute:: banner2

        A small image with guild icon, name and online member count.

    .. attribute:: banner3

        A large image with guild icon, name and online member count and a footer,
        with a "Chat Now" label on the right.

    .. attribute:: banner4

        A large image with a large Discord logo, guild icon, name and online member count,
        with a "Join My Server" label at the bottom.

.. class:: Locale

    Represents supported locales by Discord.

    .. versionadded:: 2.5

    .. attribute:: bg

        The ``bg`` (Bulgarian) locale.

    .. attribute:: cs

        The ``cs`` (Czech) locale.

    .. attribute:: da

        The ``da`` (Danish) locale.

    .. attribute:: de

        The ``de`` (German) locale.

    .. attribute:: el

        The ``el`` (Greek) locale.

    .. attribute:: en_GB

        The ``en_GB`` (English, UK) locale.

    .. attribute:: en_US

        The ``en_US`` (English, US) locale.

    .. attribute:: es_ES

        The ``es_ES`` (Spanish) locale.

    .. attribute:: fi

        The ``fi`` (Finnish) locale.

    .. attribute:: fr

        The ``fr`` (French) locale.

    .. attribute:: hi

        The ``hi`` (Hindi) locale.

    .. attribute:: hr

        The ``hr`` (Croatian) locale.

    .. attribute:: it

        The ``it`` (Italian) locale.

    .. attribute:: ja

        The ``ja`` (Japanese) locale.

    .. attribute:: ko

        The ``ko`` (Korean) locale.

    .. attribute:: lt

        The ``lt`` (Lithuanian) locale.

    .. attribute:: hu

        The ``hu`` (Hungarian) locale.

    .. attribute:: nl

        The ``nl`` (Dutch) locale.

    .. attribute:: no

        The ``no`` (Norwegian) locale.

    .. attribute:: pl

        The ``pl`` (Polish) locale.

    .. attribute:: pt_BR

        The ``pt_BR`` (Portuguese) locale.

    .. attribute:: ro

        The ``ro`` (Romanian) locale.

    .. attribute:: ru

        The ``ru`` (Russian) locale.

    .. attribute:: sv_SE

        The ``sv_SE`` (Swedish) locale.

    .. attribute:: th

        The ``th`` (Thai) locale.

    .. attribute:: tr

        The ``tr`` (Turkish) locale.

    .. attribute:: uk

        The ``uk`` (Ukrainian) locale.

    .. attribute:: vi

        The ``vi`` (Vietnamese) locale.

    .. attribute:: zh_CN

        The ``zh_CN`` (Chinese, China) locale.

    .. attribute:: zh_TW

        The ``zh_TW`` (Chinese, Taiwan) locale.

.. class:: AutoModActionType

    Represents the type of action an auto moderation rule will take upon execution.

    .. versionadded:: 2.6

    .. attribute:: block_message

        The rule will prevent matching messages from being posted.

    .. attribute:: send_alert_message

        The rule will send an alert to a specified channel.

    .. attribute:: timeout

        The rule will timeout the user that sent the message.

        .. note::
            This action type is only available for rules with trigger type
            :attr:`~AutoModTriggerType.keyword` or :attr:`~AutoModTriggerType.mention_spam`,
            and :attr:`~Permissions.moderate_members` permissions are required to use it.

.. class:: AutoModEventType

    Represents the type of event/context an auto moderation rule will be checked in.

    .. versionadded:: 2.6

    .. attribute:: message_send

        The rule will apply when a member sends or edits a message in the guild.

.. class:: AutoModTriggerType

    Represents the type of content that can trigger an auto moderation rule.

    .. versionadded:: 2.6

    .. attribute:: keyword

        The rule will filter messages based on a custom keyword list.

        This trigger type requires additional :class:`metadata <AutoModTriggerMetadata>`.

    .. attribute:: harmful_link

        The rule will filter messages containing malicious links.

    .. attribute:: spam

        The rule will filter messages suspected of being spam.

    .. attribute:: keyword_preset

        The rule will filter messages based on predefined lists containing commonly flagged words.

        This trigger type requires additional :class:`metadata <AutoModTriggerMetadata>`.

    .. attribute:: mention_spam

        The rule will filter messages based on the number of member/role mentions they contain.

        This trigger type requires additional :class:`metadata <AutoModTriggerMetadata>`.

Async Iterator
----------------

Some API functions return an "async iterator". An async iterator is something that is
capable of being used in an :ref:`async for statement <py:async for>`.

These async iterators can be used as follows: ::

    async for elem in channel.history():
        # do stuff with elem here

Certain utilities make working with async iterators easier, detailed below.

.. class:: AsyncIterator

    Represents the "AsyncIterator" concept. Note that no such class exists,
    it is purely abstract.

    .. container:: operations

        .. describe:: async for x in y

            Iterates over the contents of the async iterator.


    .. method:: next()
        :async:

        |coro|

        Advances the iterator by one, if possible. If no more items are found
        then this raises :exc:`NoMoreItems`.

    .. method:: get(**attrs)
        :async:

        |coro|

        Similar to :func:`utils.get` except run over the async iterator.

        Getting the last message by a user named 'Dave' or ``None``: ::

            msg = await channel.history().get(author__name='Dave')

    .. method:: find(predicate)
        :async:

        |coro|

        Similar to :func:`utils.find` except run over the async iterator.

        Unlike :func:`utils.find`\, the predicate provided can be a
        |coroutine_link|_.

        Getting the last audit log with a reason or ``None``: ::

            def predicate(event):
                return event.reason is not None

            event = await guild.audit_logs().find(predicate)

        :param predicate: The predicate to use. Could be a |coroutine_link|_.
        :return: The first element that returns ``True`` for the predicate or ``None``.

    .. method:: flatten()
        :async:

        |coro|

        Flattens the async iterator into a :class:`list` with all the elements.

        :return: A list of every element in the async iterator.
        :rtype: list

    .. method:: chunk(max_size)

        Collects items into chunks of up to a given maximum size.
        Another :class:`AsyncIterator` is returned which collects items into
        :class:`list`\s of a given size. The maximum chunk size must be a positive integer.

        .. versionadded:: 1.6

        Collecting groups of users: ::

            async for leader, *users in reaction.users().chunk(3):
                ...

        .. warning::

            The last chunk collected may not be as large as ``max_size``.

        :param max_size: The size of individual chunks.
        :rtype: :class:`AsyncIterator`

    .. method:: map(func)

        This is similar to the built-in :func:`map <py:map>` function. Another
        :class:`AsyncIterator` is returned that executes the function on
        every element it is iterating over. This function can either be a
        regular function or a |coroutine_link|_.

        Creating a content iterator: ::

            def transform(message):
                return message.content

            async for content in channel.history().map(transform):
                message_length = len(content)

        :param func: The function to call on every element. Could be a |coroutine_link|_.
        :rtype: :class:`AsyncIterator`

    .. method:: filter(predicate)

        This is similar to the built-in :func:`filter <py:filter>` function. Another
        :class:`AsyncIterator` is returned that filters over the original
        async iterator. This predicate can be a regular function or a |coroutine_link|_.

        Getting messages by non-bot accounts: ::

            def predicate(message):
                return not message.author.bot

            async for elem in channel.history().filter(predicate):
                ...

        :param predicate: The predicate to call on every element. Could be a |coroutine_link|_.
        :rtype: :class:`AsyncIterator`

.. _discord-api-audit-logs:

Audit Log Data
----------------

Working with :meth:`Guild.audit_logs` is a complicated process with a lot of machinery
involved. The library attempts to make it easy to use and friendly. In order to accomplish
this goal, it must make use of a couple of data classes that aid in this goal.

AuditLogEntry
~~~~~~~~~~~~~~~

.. attributetable:: AuditLogEntry

.. autoclass:: AuditLogEntry
    :members:

AuditLogChanges
~~~~~~~~~~~~~~~~~

.. attributetable:: AuditLogChanges

.. class:: AuditLogChanges

    An audit log change set.

    .. attribute:: before

        The old value. The attribute has the type of :class:`AuditLogDiff`.

        Depending on the :class:`AuditLogActionCategory` retrieved by
        :attr:`~AuditLogEntry.category`\, the data retrieved by this
        attribute differs:

        +----------------------------------------+---------------------------------------------------+
        |                Category                |                    Description                    |
        +----------------------------------------+---------------------------------------------------+
        | :attr:`~AuditLogActionCategory.create` | All attributes are set to ``None``.               |
        +----------------------------------------+---------------------------------------------------+
        | :attr:`~AuditLogActionCategory.delete` | All attributes are set the value before deletion. |
        +----------------------------------------+---------------------------------------------------+
        | :attr:`~AuditLogActionCategory.update` | All attributes are set the value before updating. |
        +----------------------------------------+---------------------------------------------------+
        | ``None``                               | No attributes are set.                            |
        +----------------------------------------+---------------------------------------------------+

    .. attribute:: after

        The new value. The attribute has the type of :class:`AuditLogDiff`.

        Depending on the :class:`AuditLogActionCategory` retrieved by
        :attr:`~AuditLogEntry.category`\, the data retrieved by this
        attribute differs:

        +----------------------------------------+--------------------------------------------------+
        |                Category                |                   Description                    |
        +----------------------------------------+--------------------------------------------------+
        | :attr:`~AuditLogActionCategory.create` | All attributes are set to the created value      |
        +----------------------------------------+--------------------------------------------------+
        | :attr:`~AuditLogActionCategory.delete` | All attributes are set to ``None``               |
        +----------------------------------------+--------------------------------------------------+
        | :attr:`~AuditLogActionCategory.update` | All attributes are set the value after updating. |
        +----------------------------------------+--------------------------------------------------+
        | ``None``                               | No attributes are set.                           |
        +----------------------------------------+--------------------------------------------------+

AuditLogDiff
~~~~~~~~~~~~~

.. attributetable:: AuditLogDiff

.. class:: AuditLogDiff

    Represents an audit log "change" object. A change object has dynamic
    attributes that depend on the type of action being done. Certain actions
    map to certain attributes being set.

    Note that accessing an attribute that does not match the specified action
    will lead to an attribute error.

    To get a list of attributes that have been set, you can iterate over
    them. To see a list of all possible attributes that could be set based
    on the action being done, check the documentation for :class:`AuditLogAction`,
    otherwise check the documentation below for all attributes that are possible.

    .. container:: operations

        .. describe:: iter(diff)

            Returns an iterator over (attribute, value) tuple of this diff.

    .. attribute:: name

        A name of something.

        :type: :class:`str`

    .. attribute:: icon

        A guild's or role's icon.

        See also :attr:`Guild.icon` or :attr:`Role.icon`.

        :type: :class:`Asset`

    .. attribute:: splash

        The guild's invite splash. See also :attr:`Guild.splash`.

        :type: :class:`Asset`

    .. attribute:: discovery_splash

        The guild's discovery splash. See also :attr:`Guild.discovery_splash`.

        :type: :class:`Asset`

    .. attribute:: banner

        The guild's banner. See also :attr:`Guild.banner`.

        :type: :class:`Asset`

    .. attribute:: owner

        The guild's owner. See also :attr:`Guild.owner`

        :type: Union[:class:`Member`, :class:`User`]

    .. attribute:: region

        The guild's voice region. See also :attr:`Guild.region`.

        :type: :class:`str`

    .. attribute:: afk_channel

        The guild's AFK channel.

        If this could not be found, then it falls back to a :class:`Object`
        with the ID being set.

        See :attr:`Guild.afk_channel`.

        :type: Union[:class:`VoiceChannel`, :class:`Object`]

    .. attribute:: system_channel

        The guild's system channel.

        If this could not be found, then it falls back to a :class:`Object`
        with the ID being set.

        See :attr:`Guild.system_channel`.

        :type: Union[:class:`TextChannel`, :class:`Object`]


    .. attribute:: rules_channel

        The guild's rules channel.

        If this could not be found then it falls back to a :class:`Object`
        with the ID being set.

        See :attr:`Guild.rules_channel`.

        :type: Union[:class:`TextChannel`, :class:`Object`]


    .. attribute:: public_updates_channel

        The guild's public updates channel.

        If this could not be found then it falls back to a :class:`Object`
        with the ID being set.

        See :attr:`Guild.public_updates_channel`.

        :type: Union[:class:`TextChannel`, :class:`Object`]

    .. attribute:: afk_timeout

        The guild's AFK timeout. See :attr:`Guild.afk_timeout`.

        :type: :class:`int`

    .. attribute:: mfa_level

        The guild's MFA level. See :attr:`Guild.mfa_level`.

        :type: :class:`int`

    .. attribute:: widget_enabled

        The guild's widget has been enabled or disabled.

        :type: :class:`bool`

    .. attribute:: widget_channel

        The widget's channel.

        If this could not be found then it falls back to a :class:`Object`
        with the ID being set.

        :type: Union[:class:`abc.GuildChannel`, :class:`Object`]

    .. attribute:: verification_level

        The guild's verification level.

        See also :attr:`Guild.verification_level`.

        :type: :class:`VerificationLevel`

    .. attribute:: premium_progress_bar_enabled

        Whether the guild's premium progress bar is enabled.

        See also :attr:`Guild.premium_progress_bar_enabled`.

        :type: :class:`bool`

    .. attribute:: default_notifications

        The guild's default notification level.

        See also :attr:`Guild.default_notifications`.

        :type: :class:`NotificationLevel`

    .. attribute:: explicit_content_filter

        The guild's content filter.

        See also :attr:`Guild.explicit_content_filter`.

        :type: :class:`ContentFilter`

    .. attribute:: default_message_notifications

        The guild's default message notification setting.

        :type: :class:`int`

    .. attribute:: vanity_url_code

        The guild's vanity URL code.

        See also :meth:`Guild.vanity_invite`, :meth:`Guild.edit`, and :attr:`Guild.vanity_url_code`.

        :type: :class:`str`

    .. attribute:: preferred_locale

        The guild's preferred locale.

        :type: :class:`Locale`

    .. attribute:: position

        The position of a :class:`Role` or :class:`abc.GuildChannel`.

        :type: :class:`int`

    .. attribute:: type

        The type of channel/thread, sticker, webhook, integration (:class:`str`), or permission overwrite (:class:`int`).

        :type: Union[:class:`ChannelType`, :class:`StickerType`, :class:`WebhookType`, :class:`str`, :class:`int`]

    .. attribute:: topic

        The topic of a :class:`TextChannel`, :class:`StageChannel`, :class:`StageInstance` or :class:`ForumChannel`.

        See also :attr:`TextChannel.topic`, :attr:`StageChannel.topic`,
        :attr:`StageInstance.topic` or :attr:`ForumChannel.topic`.

        :type: :class:`str`

    .. attribute:: bitrate

        The bitrate of a :class:`VoiceChannel` or :class:`StageChannel`.

        See also :attr:`VoiceChannel.bitrate` or :attr:`StageChannel.bitrate`.

        :type: :class:`int`

    .. attribute:: overwrites

        A list of permission overwrite tuples that represents a target and a
        :class:`PermissionOverwrite` for said target.

        The first element is the object being targeted, which can either
        be a :class:`Member` or :class:`User` or :class:`Role`. If this object
        is not found then it is a :class:`Object` with an ID being filled and
        a ``type`` attribute set to either ``'role'`` or ``'member'`` to help
        decide what type of ID it is.

        :type: List[Tuple[Union[:class:`Member`, :class:`User`, :class:`Role`, :class:`Object`], :class:`PermissionOverwrite`]]

    .. attribute:: privacy_level

        The privacy level of the stage instance or guild scheduled event.

        :type: Union[:class:`StagePrivacyLevel`, :class:`GuildScheduledEventPrivacyLevel`]

    .. attribute:: roles

        A list of roles being added or removed from a member.

        If a role is not found then it is a :class:`Object` with the ID and name being
        filled in.

        :type: List[Union[:class:`Role`, :class:`Object`]]

    .. attribute:: nick

        The nickname of a member.

        See also :attr:`Member.nick`

        :type: Optional[:class:`str`]

    .. attribute:: deaf

        Whether the member is being server deafened.

        See also :attr:`VoiceState.deaf`.

        :type: :class:`bool`

    .. attribute:: mute

        Whether the member is being server muted.

        See also :attr:`VoiceState.mute`.

        :type: :class:`bool`

    .. attribute:: permissions

        The permissions of a role.

        See also :attr:`Role.permissions`.

        :type: :class:`Permissions`

    .. attribute:: colour
                   color

        The colour of a role.

        See also :attr:`Role.colour`

        :type: :class:`Colour`

    .. attribute:: hoist

        Whether the role is being hoisted or not.

        See also :attr:`Role.hoist`

        :type: :class:`bool`

    .. attribute:: mentionable

        Whether the role is mentionable or not.

        See also :attr:`Role.mentionable`

        :type: :class:`bool`

    .. attribute:: code

        The invite's code.

        See also :attr:`Invite.code`

        :type: :class:`str`

    .. attribute:: channel

        A guild channel.

        If the channel is not found then it is a :class:`Object` with the ID
        being set. In some cases the channel name is also set.

        :type: Union[:class:`abc.GuildChannel`, :class:`Object`]

    .. attribute:: inviter

        The user who created the invite.

        See also :attr:`Invite.inviter`.

        :type: Optional[:class:`User`]

    .. attribute:: max_uses

        The invite's max uses.

        See also :attr:`Invite.max_uses`.

        :type: :class:`int`

    .. attribute:: uses

        The invite's current uses.

        See also :attr:`Invite.uses`.

        :type: :class:`int`

    .. attribute:: max_age

        The invite's max age in seconds.

        See also :attr:`Invite.max_age`.

        :type: :class:`int`

    .. attribute:: temporary

        If the invite is a temporary invite.

        See also :attr:`Invite.temporary`.

        :type: :class:`bool`

    .. attribute:: allow
                   deny

        The permissions being allowed or denied.

        :type: :class:`Permissions`

    .. attribute:: id

        The ID of the object being changed.

        :type: :class:`int`

    .. attribute:: avatar

        The avatar of a member.

        See also :attr:`User.avatar`.

        :type: :class:`Asset`

    .. attribute:: slowmode_delay

        The number of seconds members have to wait before
        sending another message or creating another thread in the channel.

        See also :attr:`TextChannel.slowmode_delay`, :attr:`VoiceChannel.slowmode_delay`,
        :attr:`ForumChannel.slowmode_delay` or :attr:`Thread.slowmode_delay`.

        :type: :class:`int`

    .. attribute:: rtc_region

        The region for the voice or stage channel's voice communication.
        A value of ``None`` indicates automatic voice region detection.

        See also :attr:`VoiceChannel.rtc_region` or :attr:`StageChannel.rtc_region`.

        :type: :class:`str`

    .. attribute:: video_quality_mode

        The camera video quality for the voice or stage channel's participants.

        See also :attr:`VoiceChannel.video_quality_mode` or :attr:`StageChannel.video_quality_mode`.

        :type: :class:`VideoQualityMode`

    .. attribute:: user_limit

        The voice channel's user limit.

        See also :attr:`VoiceChannel.user_limit`.

        :type: :class:`int`

    .. attribute:: nsfw

        Whether the channel is marked as "not safe for work".

        See also :attr:`TextChannel.nsfw`, :attr:`VoiceChannel.nsfw` or :attr:`ForumChannel.nsfw`.

        :type: :class:`bool`

    .. attribute:: format_type

        The format type of a sticker being changed.

        See also :attr:`GuildSticker.format`

        :type: :class:`StickerFormatType`

    .. attribute:: emoji

        The name of the sticker's or role's emoji being changed.

        See also :attr:`GuildSticker.emoji` or :attr:`Role.emoji`.

        :type: :class:`str`

    .. attribute:: description

        The description of a guild, sticker or a guild scheduled event being changed.

        See also :attr:`Guild.description`, :attr:`GuildSticker.description`, :attr:`GuildScheduledEvent.description`

        :type: :class:`str`

    .. attribute:: available

        The availability of a sticker being changed.

        See also :attr:`GuildSticker.available`

        :type: :class:`bool`

    .. attribute:: archived

        The thread is now archived.

        :type: :class:`bool`

    .. attribute:: locked

        The thread is being locked or unlocked.

        :type: :class:`bool`

    .. attribute:: auto_archive_duration

        The thread's auto archive duration being changed.

        See also :attr:`Thread.auto_archive_duration`

        :type: :class:`int`

    .. attribute:: default_auto_archive_duration

        The default auto archive duration for newly created threads being changed.

        :type: :class:`int`

    .. attribute:: invitable

        Whether non-moderators can add other non-moderators to the thread.

        :type: :class:`bool`

    .. attribute:: timeout

        The datetime when the timeout expires, if any.

        :type: :class:`datetime.datetime`

    .. attribute:: entity_type

        The entity type of a guild scheduled event being changed.

        :type: :class:`GuildScheduledEventEntityType`

    .. attribute:: location

        The location of a guild scheduled event being changed.

        :type: :class:`str`

    .. attribute:: status

        The status of a guild scheduled event being changed.

        :type: :class:`GuildScheduledEventStatus`

    .. attribute:: image

        The cover image of a guild scheduled event being changed.

        :type: :class:`Asset`

    .. attribute:: command_permissions

        A mapping of target ID to guild permissions of an application command.

        Note that only changed permission entries are included,
        not necessarily all of the command's permissions.

        :type: Dict[:class:`int`, :class:`ApplicationCommandPermissions`]

    .. attribute:: application_id

        The ID of the application that created a webhook.

        :type: :class:`int`

    .. attribute:: flags

        The channel's flags.

        See also :attr:`abc.GuildChannel.flags` or :attr:`Thread.flags`.

        :type: :class:`ChannelFlags`

    .. attribute:: system_channel_flags

        The guild's system channel settings.

        See also :attr:`Guild.system_channel_flags`.

        :type: :class:`SystemChannelFlags`

    .. attribute:: enabled

        Whether something was enabled or disabled.

        :type: :class:`bool`

    .. attribute:: trigger_type

        The trigger type of an auto moderation rule being changed.

        :type: :class:`AutoModTriggerType`

    .. attribute:: event_type

        The event type of an auto moderation rule being changed.

        :type: :class:`AutoModEventType`

    .. attribute:: actions

        The list of actions of an auto moderation rule being changed.

        :type: List[:class:`AutoModAction`]

    .. attribute:: trigger_metadata

        The additional trigger metadata of an auto moderation rule being changed.

        :type: :class:`AutoModTriggerMetadata`

    .. attribute:: exempt_roles

        The list of roles that are exempt from an auto moderation rule being changed.

        If a role is not found then it is an :class:`Object` with the ID being set.

        :type: List[Union[:class:`Role`, :class:`Object`]]

    .. attribute:: exempt_channels

        The list of channels that are exempt from an auto moderation rule being changed.

        If a channel is not found then it is an :class:`Object` with the ID being set.

        :type: List[Union[:class:`abc.GuildChannel`, :class:`Object`]]

Webhook Support
------------------

disnake offers support for creating, editing, and executing webhooks through the :class:`Webhook` class.

Webhook
~~~~~~~~~

.. attributetable:: Webhook

.. autoclass:: Webhook()
    :members:
    :inherited-members:

WebhookMessage
~~~~~~~~~~~~~~~~

.. attributetable:: WebhookMessage

.. autoclass:: WebhookMessage()
    :members:

SyncWebhook
~~~~~~~~~~~~

.. attributetable:: SyncWebhook

.. autoclass:: SyncWebhook()
    :members:
    :inherited-members:

SyncWebhookMessage
~~~~~~~~~~~~~~~~~~~

.. attributetable:: SyncWebhookMessage

.. autoclass:: SyncWebhookMessage()
    :members:

.. _discord_api_abcs:

Abstract Base Classes
-----------------------

An :term:`abstract base class` (also known as an ``abc``) is a class that models can inherit
to get their behaviour. **Abstract base classes should not be instantiated**.
They are mainly there for usage with :func:`isinstance` and :func:`issubclass`\.

This library has a module related to abstract base classes, in which all the ABCs are subclasses of
:class:`typing.Protocol`.

Snowflake
~~~~~~~~~~

.. attributetable:: disnake.abc.Snowflake

.. autoclass:: disnake.abc.Snowflake()
    :members:

User
~~~~~

.. attributetable:: disnake.abc.User

.. autoclass:: disnake.abc.User()
    :members:

PrivateChannel
~~~~~~~~~~~~~~~

.. attributetable:: disnake.abc.PrivateChannel

.. autoclass:: disnake.abc.PrivateChannel()
    :members:

GuildChannel
~~~~~~~~~~~~~

.. attributetable:: disnake.abc.GuildChannel

.. autoclass:: disnake.abc.GuildChannel()
    :members:

Messageable
~~~~~~~~~~~~

.. attributetable:: disnake.abc.Messageable

.. autoclass:: disnake.abc.Messageable()
    :members:
    :exclude-members: history, typing

    .. automethod:: disnake.abc.Messageable.history
        :async-for:

    .. automethod:: disnake.abc.Messageable.typing
        :async-with:

Connectable
~~~~~~~~~~~~

.. attributetable:: disnake.abc.Connectable

.. autoclass:: disnake.abc.Connectable()

.. _discord_api_models:

Discord Models
---------------

Models are classes that are received from Discord and are not meant to be created by
the user of the library.

.. danger::

    The classes listed below are **not intended to be created by users** and are also
    **read-only**.

    For example, this means that you should not make your own :class:`User` instances
    nor should you modify the :class:`User` instance yourself.

    If you want to get one of these model classes instances they'd have to be through
    the cache, and a common way of doing so is through the :func:`utils.find` function
    or attributes of model classes that you receive from the events specified in the
    :ref:`discord-api-events`.

.. note::

    Nearly all classes here have :ref:`py:slots` defined which means that it is
    impossible to have dynamic attributes to the data classes.


ClientUser
~~~~~~~~~~~~

.. attributetable:: ClientUser

.. autoclass:: ClientUser()
    :members:
    :inherited-members:

User
~~~~~

.. attributetable:: User

.. autoclass:: User()
    :members:
    :inherited-members:
    :exclude-members: history, typing

    .. automethod:: history
        :async-for:

    .. automethod:: typing
        :async-with:

Attachment
~~~~~~~~~~~

.. attributetable:: Attachment

.. autoclass:: Attachment()
    :members:

Asset
~~~~~

.. attributetable:: Asset

.. autoclass:: Asset()
    :members:
    :inherited-members:

Message
~~~~~~~

.. attributetable:: Message

.. autoclass:: Message()
    :members:

APISlashCommand
~~~~~~~~~~~~~~~

.. attributetable:: APISlashCommand

.. autoclass:: APISlashCommand()
    :members:
    :inherited-members:

APIUserCommand
~~~~~~~~~~~~~~

.. attributetable:: APIUserCommand

.. autoclass:: APIUserCommand()
    :members:
    :inherited-members:

APIMessageCommand
~~~~~~~~~~~~~~~~~

.. attributetable:: APIMessageCommand

.. autoclass:: APIMessageCommand()
    :members:
    :inherited-members:

ApplicationCommandPermissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: ApplicationCommandPermissions

.. autoclass:: ApplicationCommandPermissions()
    :members:

GuildApplicationCommandPermissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: GuildApplicationCommandPermissions

.. autoclass:: GuildApplicationCommandPermissions()
    :members:

Component
~~~~~~~~~~

.. attributetable:: Component

.. autoclass:: Component()
    :members:

ActionRow
~~~~~~~~~~

.. attributetable:: ActionRow

.. autoclass:: ActionRow()
    :members:

Button
~~~~~~~

.. attributetable:: Button

.. autoclass:: Button()
    :members:
    :inherited-members:

SelectMenu
~~~~~~~~~~~

.. attributetable:: SelectMenu

.. autoclass:: SelectMenu()
    :members:
    :inherited-members:

TextInput
~~~~~~~~~

.. attributetable:: TextInput

.. autoclass:: TextInput()
    :members:
    :inherited-members:


DeletedReferencedMessage
~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: DeletedReferencedMessage

.. autoclass:: DeletedReferencedMessage()
    :members:


Reaction
~~~~~~~~~

.. attributetable:: Reaction

.. autoclass:: Reaction()
    :members:
    :exclude-members: users

    .. automethod:: users
        :async-for:

Guild
~~~~~~

.. attributetable:: Guild

.. autoclass:: Guild()
    :members:
    :exclude-members: fetch_members, audit_logs

    .. automethod:: fetch_members
        :async-for:

    .. automethod:: audit_logs
        :async-for:

.. class:: BanEntry

    A namedtuple which represents a ban returned from :meth:`~Guild.bans`.

    .. attribute:: reason

        The reason this user was banned.

        :type: Optional[:class:`str`]
    .. attribute:: user

        The :class:`User` that was banned.

        :type: :class:`User`

GuildPreview
~~~~~~~~~~~~~

.. attributetable:: GuildPreview

.. autoclass:: GuildPreview()
    :members:


GuildScheduledEvent
~~~~~~~~~~~~~~~~~~~~

.. attributetable:: GuildScheduledEvent

.. autoclass:: GuildScheduledEvent()
    :members:

GuildScheduledEventMetadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: GuildScheduledEventMetadata

.. autoclass:: GuildScheduledEventMetadata()
    :members:


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

Interaction
~~~~~~~~~~~~

.. attributetable:: Interaction

.. autoclass:: Interaction()
    :members:
    :inherited-members:
    :exclude-members: original_message, edit_original_message, delete_original_message

ApplicationCommandInteraction
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: ApplicationCommandInteraction

.. autoclass:: ApplicationCommandInteraction()
    :members:
    :inherited-members:

GuildCommandInteraction
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: GuildCommandInteraction()

UserCommandInteraction
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: UserCommandInteraction()

MessageCommandInteraction
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: MessageCommandInteraction()

MessageInteraction
~~~~~~~~~~~~~~~~~~

.. attributetable:: MessageInteraction

.. autoclass:: MessageInteraction()
    :members:
    :inherited-members:

ModalInteraction
~~~~~~~~~~~~~~~~

.. attributetable:: ModalInteraction

.. autoclass:: ModalInteraction()
    :members:
    :inherited-members:

InteractionResponse
~~~~~~~~~~~~~~~~~~~~

.. attributetable:: InteractionResponse

.. autoclass:: InteractionResponse()
    :members:

InteractionMessage
~~~~~~~~~~~~~~~~~~~

.. attributetable:: InteractionMessage

.. autoclass:: InteractionMessage()
    :members:
    :inherited-members:

ApplicationCommandInteractionData
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: ApplicationCommandInteractionData

.. autoclass:: ApplicationCommandInteractionData()
    :members:

ApplicationCommandInteractionDataOption
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: ApplicationCommandInteractionDataOption

.. autoclass:: ApplicationCommandInteractionDataOption()
    :members:

ApplicationCommandInteractionDataResolved
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: ApplicationCommandInteractionDataResolved

.. autoclass:: ApplicationCommandInteractionDataResolved()
    :members:

MessageInteractionData
~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: MessageInteractionData

.. autoclass:: MessageInteractionData()
    :members:

ModalInteractionData
~~~~~~~~~~~~~~~~~~~~

.. attributetable:: ModalInteractionData

.. autoclass:: ModalInteractionData()
    :members:

Member
~~~~~~

.. attributetable:: Member

.. autoclass:: Member()
    :members:
    :inherited-members:
    :exclude-members: history, typing

    .. automethod:: history
        :async-for:

    .. automethod:: typing
        :async-with:

Spotify
~~~~~~~~

.. attributetable:: Spotify

.. autoclass:: Spotify()
    :members:
    :inherited-members:

VoiceState
~~~~~~~~~~~

.. attributetable:: VoiceState

.. autoclass:: VoiceState()
    :members:

Emoji
~~~~~

.. attributetable:: Emoji

.. autoclass:: Emoji()
    :members:
    :inherited-members:

PartialEmoji
~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: PartialEmoji

.. autoclass:: PartialEmoji()
    :members:
    :inherited-members:

Role
~~~~~

.. attributetable:: Role

.. autoclass:: Role()
    :members:

RoleTags
~~~~~~~~~~

.. attributetable:: RoleTags

.. autoclass:: RoleTags()
    :members:

PartialMessageable
~~~~~~~~~~~~~~~~~~~~

.. attributetable:: PartialMessageable

.. autoclass:: PartialMessageable()
    :members:
    :inherited-members:

TextChannel
~~~~~~~~~~~~

.. attributetable:: TextChannel

.. autoclass:: TextChannel()
    :members:
    :inherited-members:
    :exclude-members: history, typing

    .. automethod:: history
        :async-for:

    .. automethod:: typing
        :async-with:

Thread
~~~~~~~~

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
~~~~~~~~~~~~~

.. attributetable:: ThreadMember

.. autoclass:: ThreadMember()
    :members:

VoiceChannel
~~~~~~~~~~~~~

.. attributetable:: VoiceChannel

.. autoclass:: VoiceChannel()
    :members:
    :inherited-members:

StageChannel
~~~~~~~~~~~~~

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

StageInstance
~~~~~~~~~~~~~~

.. attributetable:: StageInstance

.. autoclass:: StageInstance()
    :members:

CategoryChannel
~~~~~~~~~~~~~~~~~

.. attributetable:: CategoryChannel

.. autoclass:: CategoryChannel()
    :members:
    :inherited-members:

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

PartialInviteGuild
~~~~~~~~~~~~~~~~~~~

.. attributetable:: PartialInviteGuild

.. autoclass:: PartialInviteGuild()
    :members:

PartialInviteChannel
~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: PartialInviteChannel

.. autoclass:: PartialInviteChannel()
    :members:

Invite
~~~~~~~

.. attributetable:: Invite

.. autoclass:: Invite()
    :members:

Template
~~~~~~~~~

.. attributetable:: Template

.. autoclass:: Template()
    :members:

WidgetChannel
~~~~~~~~~~~~~~~

.. attributetable:: WidgetChannel

.. autoclass:: WidgetChannel()
    :members:

WidgetMember
~~~~~~~~~~~~~

.. attributetable:: WidgetMember

.. autoclass:: WidgetMember()
    :members:
    :inherited-members:
    :exclude-members: public_flags, default_avatar, banner, accent_colour, accent_color, colour, color, mention, created_at, mentioned_in

WidgetSettings
~~~~~~~~~~~~~~

.. attributetable:: WidgetSettings

.. autoclass:: WidgetSettings()
    :members:

Widget
~~~~~~~

.. attributetable:: Widget

.. autoclass:: Widget()
    :members:

WelcomeScreen
~~~~~~~~~~~~~~

.. attributetable:: WelcomeScreen

.. autoclass:: WelcomeScreen()
    :members:

WelcomeScreenChannel
~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: WelcomeScreenChannel

.. autoclass:: WelcomeScreenChannel()

VoiceRegion
~~~~~~~~~~~

.. attributetable:: VoiceRegion

.. autoclass:: VoiceRegion()
    :members:

StickerPack
~~~~~~~~~~~~~

.. attributetable:: StickerPack

.. autoclass:: StickerPack()
    :members:

StickerItem
~~~~~~~~~~~~~

.. attributetable:: StickerItem

.. autoclass:: StickerItem()
    :members:
    :inherited-members:

Sticker
~~~~~~~~~~~~~~~

.. attributetable:: Sticker

.. autoclass:: Sticker()
    :members:
    :inherited-members:

StandardSticker
~~~~~~~~~~~~~~~~

.. attributetable:: StandardSticker

.. autoclass:: StandardSticker()
    :members:
    :inherited-members:

GuildSticker
~~~~~~~~~~~~~

.. attributetable:: GuildSticker

.. autoclass:: GuildSticker()
    :members:
    :inherited-members:

AutoModRule
~~~~~~~~~~~~

.. attributetable:: AutoModRule

.. autoclass:: AutoModRule()
    :members:

AutoModActionExecution
~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: AutoModActionExecution

.. autoclass:: AutoModActionExecution()
    :members:

RawMessageDeleteEvent
~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: RawMessageDeleteEvent

.. autoclass:: RawMessageDeleteEvent()
    :members:

RawBulkMessageDeleteEvent
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: RawBulkMessageDeleteEvent

.. autoclass:: RawBulkMessageDeleteEvent()
    :members:

RawMessageUpdateEvent
~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: RawMessageUpdateEvent

.. autoclass:: RawMessageUpdateEvent()
    :members:

RawReactionActionEvent
~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: RawReactionActionEvent

.. autoclass:: RawReactionActionEvent()
    :members:

RawReactionClearEvent
~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: RawReactionClearEvent

.. autoclass:: RawReactionClearEvent()
    :members:

RawReactionClearEmojiEvent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: RawReactionClearEmojiEvent

.. autoclass:: RawReactionClearEmojiEvent()
    :members:

RawIntegrationDeleteEvent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: RawIntegrationDeleteEvent

.. autoclass:: RawIntegrationDeleteEvent()
    :members:

RawGuildScheduledEventUserActionEvent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: RawGuildScheduledEventUserActionEvent

.. autoclass:: RawGuildScheduledEventUserActionEvent()
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

RawTypingEvent
~~~~~~~~~~~~~~

.. attributetable:: RawTypingEvent

.. autoclass:: RawTypingEvent()
    :members:

RawGuildMemberRemoveEvent
~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: RawGuildMemberRemoveEvent

.. autoclass:: RawGuildMemberRemoveEvent()
    :members:

PartialWebhookGuild
~~~~~~~~~~~~~~~~~~~~

.. attributetable:: PartialWebhookGuild

.. autoclass:: PartialWebhookGuild()
    :members:

PartialWebhookChannel
~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: PartialWebhookChannel

.. autoclass:: PartialWebhookChannel()
    :members:

.. _discord_api_data:

Data Classes
--------------

Some classes are just there to be data containers, this lists them.

Unlike :ref:`models <discord_api_models>` you are allowed to create
most of these yourself, even if they can also be used to hold attributes.

Nearly all classes here have :ref:`py:slots` defined which means that it is
impossible to have dynamic attributes to the data classes.

The only exception to this rule is :class:`Object`, which is made with
dynamic attributes in mind.


Object
~~~~~~~

.. attributetable:: Object

.. autoclass:: Object
    :members:

Embed
~~~~~~

.. attributetable:: Embed

.. autoclass:: Embed
    :members:

AllowedMentions
~~~~~~~~~~~~~~~~~

.. attributetable:: AllowedMentions

.. autoclass:: AllowedMentions
    :members:

MessageReference
~~~~~~~~~~~~~~~~~

.. attributetable:: MessageReference

.. autoclass:: MessageReference
    :members:

InteractionReference
~~~~~~~~~~~~~~~~~~~~

.. attributetable:: InteractionReference

.. autoclass:: InteractionReference
    :members:

PartialMessage
~~~~~~~~~~~~~~~~~

.. attributetable:: PartialMessage

.. autoclass:: PartialMessage
    :members:

ApplicationCommand
~~~~~~~~~~~~~~~~~~

.. attributetable:: ApplicationCommand

.. autoclass:: ApplicationCommand()
    :members:

SlashCommand
~~~~~~~~~~~~

.. attributetable:: SlashCommand

.. autoclass:: SlashCommand()
    :members:
    :inherited-members:

UserCommand
~~~~~~~~~~~

.. attributetable:: UserCommand

.. autoclass:: UserCommand()
    :members:
    :inherited-members:

MessageCommand
~~~~~~~~~~~~~~

.. attributetable:: MessageCommand

.. autoclass:: MessageCommand()
    :members:
    :inherited-members:

Option
~~~~~~

.. attributetable:: Option

.. autoclass:: Option()
    :members:

OptionChoice
~~~~~~~~~~~~

.. attributetable:: OptionChoice

.. autoclass:: OptionChoice()
    :members:

SelectOption
~~~~~~~~~~~~~

.. attributetable:: SelectOption

.. autoclass:: SelectOption
    :members:

Intents
~~~~~~~~~~

.. attributetable:: Intents

.. autoclass:: Intents
    :members:

MemberCacheFlags
~~~~~~~~~~~~~~~~~~

.. attributetable:: MemberCacheFlags

.. autoclass:: MemberCacheFlags
    :members:

ApplicationFlags
~~~~~~~~~~~~~~~~~

.. attributetable:: ApplicationFlags

.. autoclass:: ApplicationFlags
    :members:

ChannelFlags
~~~~~~~~~~~~

.. attributetable:: ChannelFlags

.. autoclass:: ChannelFlags
    :members:

AutoModKeywordPresets
~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: AutoModKeywordPresets

.. autoclass:: AutoModKeywordPresets
    :members:

AutoModTriggerMetadata
~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: AutoModTriggerMetadata

.. autoclass:: AutoModTriggerMetadata
    :members:

AutoModAction
~~~~~~~~~~~~~~

.. attributetable:: AutoModAction

.. autoclass:: AutoModAction()
    :members:

AutoModBlockMessageAction
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: AutoModBlockMessageAction

.. autoclass:: AutoModBlockMessageAction
    :members:

AutoModSendAlertAction
~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: AutoModSendAlertAction

.. autoclass:: AutoModSendAlertAction
    :members:

AutoModTimeoutAction
~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: AutoModTimeoutAction

.. autoclass:: AutoModTimeoutAction
    :members:

File
~~~~~

.. attributetable:: File

.. autoclass:: File
    :members:

Colour
~~~~~~

.. attributetable:: Colour

.. autoclass:: Colour
    :members:

BaseActivity
~~~~~~~~~~~~~~

.. attributetable:: BaseActivity

.. autoclass:: BaseActivity
    :members:
    :inherited-members:

Activity
~~~~~~~~~

.. attributetable:: Activity

.. autoclass:: Activity
    :members:
    :inherited-members:

Game
~~~~~

.. attributetable:: Game

.. autoclass:: Game
    :members:
    :inherited-members:

Streaming
~~~~~~~~~~~

.. attributetable:: Streaming

.. autoclass:: Streaming
    :members:
    :inherited-members:

CustomActivity
~~~~~~~~~~~~~~~

.. attributetable:: CustomActivity

.. autoclass:: CustomActivity
    :members:
    :inherited-members:

Permissions
~~~~~~~~~~~~

.. attributetable:: Permissions

.. autoclass:: Permissions
    :members:

PermissionOverwrite
~~~~~~~~~~~~~~~~~~~~

.. attributetable:: PermissionOverwrite

.. autoclass:: PermissionOverwrite
    :members:

ShardInfo
~~~~~~~~~~~

.. attributetable:: ShardInfo

.. autoclass:: ShardInfo()
    :members:

SessionStartLimit
~~~~~~~~~~~~~~~~~

.. attributetable:: SessionStartLimit

.. autoclass:: SessionStartLimit()
    :members:

GatewayParams
~~~~~~~~~~~~~~

.. attributetable:: GatewayParams

.. autoclass:: GatewayParams()
    :members:
    :exclude-members: encoding, zlib

SystemChannelFlags
~~~~~~~~~~~~~~~~~~~~

.. attributetable:: SystemChannelFlags

.. autoclass:: SystemChannelFlags()
    :members:

MessageFlags
~~~~~~~~~~~~

.. attributetable:: MessageFlags

.. autoclass:: MessageFlags()
    :members:

PublicUserFlags
~~~~~~~~~~~~~~~

.. attributetable:: PublicUserFlags

.. autoclass:: PublicUserFlags()
    :members:

.. _discord_ui_kit:

Bot UI Kit
-------------

The library has helpers to help create component-based UIs.

View
~~~~~~~

.. attributetable:: disnake.ui.View

.. autoclass:: disnake.ui.View
    :members:

ActionRow
~~~~~~~~~~

.. attributetable:: disnake.ui.ActionRow

.. autoclass:: disnake.ui.ActionRow
    :members:

Item
~~~~~~~

.. attributetable:: disnake.ui.Item

.. autoclass:: disnake.ui.Item
    :members:

WrappedComponent
~~~~~~~~~~~~~~~~

.. attributetable:: disnake.ui.WrappedComponent

.. autoclass:: disnake.ui.WrappedComponent
    :members:

Button
~~~~~~~

.. attributetable:: disnake.ui.Button

.. autoclass:: disnake.ui.Button
    :members:
    :inherited-members:

.. autofunction:: disnake.ui.button(cls=disnake.ui.Button, *, style=ButtonStyle.secondary, label=None, disabled=False, custom_id=..., url=None, emoji=None, row=None)

Select
~~~~~~~

.. attributetable:: disnake.ui.Select

.. autoclass:: disnake.ui.Select
    :members:
    :inherited-members:

.. autofunction:: disnake.ui.select(cls=disnake.ui.Select, *, custom_id=..., placeholder=None, min_values=1, max_values=1, options=..., disabled=False, row=None)

Modal
~~~~~

.. attributetable:: disnake.ui.Modal

.. autoclass:: disnake.ui.Modal
    :members:

TextInput
~~~~~~~~~

.. attributetable:: disnake.ui.TextInput

.. autoclass:: disnake.ui.TextInput
    :members:


Localization
------------

The library uses the following types/methods to support localization.

Localized
~~~~~~~~~

.. autoclass:: Localized
    :members:
    :inherited-members:

LocalizationValue
~~~~~~~~~~~~~~~~~

.. autoclass:: LocalizationValue
    :members:
    :inherited-members:

LocalizationProtocol
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: LocalizationProtocol
    :members:

LocalizationStore
~~~~~~~~~~~~~~~~~~

.. autoclass:: LocalizationStore
    :members:
    :inherited-members:


Exceptions
------------

The following exceptions are thrown by the library.

.. autoexception:: DiscordException

.. autoexception:: ClientException

.. autoexception:: LoginFailure

.. autoexception:: NoMoreItems

.. autoexception:: HTTPException
    :members:

.. autoexception:: Forbidden

.. autoexception:: NotFound

.. autoexception:: DiscordServerError

.. autoexception:: InvalidData

.. autoexception:: WebhookTokenMissing

.. autoexception:: GatewayNotFound

.. autoexception:: ConnectionClosed

.. autoexception:: PrivilegedIntentsRequired

.. autoexception:: SessionStartLimitReached

.. autoexception:: InteractionException

.. autoexception:: InteractionResponded

.. autoexception:: InteractionNotResponded

.. autoexception:: InteractionTimedOut

.. autoexception:: ModalChainNotSupported

.. autoexception:: LocalizationKeyError

.. autoexception:: disnake.opus.OpusError

.. autoexception:: disnake.opus.OpusNotLoaded

Exception Hierarchy
~~~~~~~~~~~~~~~~~~~~~

.. exception_hierarchy::

    - :exc:`Exception`
        - :exc:`DiscordException`
            - :exc:`ClientException`
                - :exc:`InvalidData`
                - :exc:`LoginFailure`
                - :exc:`ConnectionClosed`
                - :exc:`PrivilegedIntentsRequired`
                - :exc:`SessionStartLimitReached`
                - :exc:`InteractionException`
                    - :exc:`InteractionResponded`
                    - :exc:`InteractionNotResponded`
                    - :exc:`InteractionTimedOut`
                    - :exc:`ModalChainNotSupported`
            - :exc:`NoMoreItems`
            - :exc:`GatewayNotFound`
            - :exc:`HTTPException`
                - :exc:`Forbidden`
                - :exc:`NotFound`
                - :exc:`DiscordServerError`
            - :exc:`LocalizationKeyError`
            - :exc:`WebhookTokenMissing`


Warnings
----------

.. autoclass:: DiscordWarning

.. autoclass:: ConfigWarning

.. autoclass:: SyncWarning

.. autoclass:: LocalizationWarning

Warning Hierarchy
~~~~~~~~~~~~~~~~~~~

.. exception_hierarchy::

    - :class:`DiscordWarning`
        - :class:`ConfigWarning`
        - :class:`SyncWarning`
        - :class:`LocalizationWarning`
