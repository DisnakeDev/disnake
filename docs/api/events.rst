.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

.. _disnake_api_events:

Events
======

This section documents events related to the main library.

What are events?
----------------

So, what are events anyway? Most of the :class:`Client` application cycle is based on *events* - special "notifications" usually sent by Discord
to notify client about certain actions like message deletion, emoji creation, member nickname updates, etc.

This library provides a few ways to register an
*event handler* — a special function which will listen for specific types of events — which allows you to take action based on certain events.

The first way is through the use of the :meth:`Client.event` decorator: ::

    client = disnake.Client(...)

    @client.event
    async def on_message(message):
        if message.author.bot:
            return

        if message.content.startswith('$hello'):
            await message.reply(f'Hello, {message.author}!')

The second way is through subclassing :class:`Client` and
overriding the specific events. For example: ::

    class MyClient(disnake.Client):
        async def on_message(self, message):
            if message.author.bot:
                return

            if message.content.startswith('$hello'):
                await message.reply(f'Hello, {message.author}!')

Another way is to use :meth:`Client.wait_for`, which is a single-use event handler to wait for
something to happen in more specific scenarios: ::

    @client.event
    async def on_message(message):
        if message.content.startswith('$greet'):
            channel = message.channel
            await channel.send('Say hello!')

            def check(m):
                return m.content == 'hello' and m.channel == channel

            # wait for a message that passes the check
            msg = await client.wait_for('message', check=check)
            await channel.send(f'Hello {msg.author}!')

The above pieces of code are essentially equal, and both respond with ``Hello, {author's username here}!`` message
when a user sends a ``$hello`` message.

.. warning::

    Event handlers described here are a bit different from :class:`~ext.commands.Bot`'s *event listeners*.

    :class:`Client`'s event handlers are unique, which means you can only have one of each type (i.e. only one `on_message`, one `on_member_ban`, etc.). With :class:`~ext.commands.Bot` however, you can have as many *listeners*
    of the same type as you want.

    Also note that :meth:`Bot.event() <disnake.ext.commands.Bot.event>` is the same as :class:`Client`'s
    :meth:`~Client.event` (since :class:`~ext.commands.Bot` subclasses :class:`Client`) and does not allow to listen/watch
    for multiple events of the same type. Consider using :meth:`Bot.listen() <disnake.ext.commands.Bot.listen>` instead.

.. note::

    Events can be sent not only by Discord. For instance, if you use the :ref:`commands extension <disnake_ext_commands>`,
    you'll also receive various events related to your commands' execution process.

If an event handler raises an exception, :func:`on_error` will be called
to handle it, which defaults to printing a traceback and ignoring the exception.

.. warning::

    Every event handler/listener must be a |coroutine_link|_. In order to turn a function into a coroutine, they must be ``async def`` functions.

Reference
---------

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
        :ref:`ext_commands_api_bots` listeners such as
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
        :ref:`ext_commands_api_bots` listeners such as
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

Audit Logs
++++++++++

.. function:: on_audit_log_entry_create(entry)

    Called when an audit log entry is created.
    You must have the :attr:`~Permissions.view_audit_log` permission to receive this.

    This requires :attr:`Intents.moderation` to be enabled.

    .. warning::
        This scope of data in this gateway event is limited, which means it is much more
        reliant on the cache than :meth:`Guild.audit_logs`.
        Because of this, :attr:`AuditLogEntry.target` and :attr:`AuditLogEntry.user`
        will frequently be of type :class:`Object` instead of the respective model.

    .. versionadded:: 2.8

    :param entry: The audit log entry that was created.
    :type entry: :class:`AuditLogEntry`

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

    Called when a :class:`Member` is updated in a :class:`Guild`. This will also be called
    when a :class:`User` object linked to a guild :class:`Member` changes.
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

    Called when a :class:`Member` is updated in a :class:`Guild`. This will also be called
    when a :class:`User` object linked to a guild :class:`Member` changes.
    Unlike :func:`on_member_update`, this is called regardless of the member cache.

    .. versionadded:: 2.6

    :param member: The member that was updated.
    :type member: :class:`Member`

.. function:: on_member_ban(guild, user)

    Called when user gets banned from a :class:`Guild`.

    This requires :attr:`Intents.moderation` to be enabled.

    :param guild: The guild the user got banned from.
    :type guild: :class:`Guild`
    :param user: The user that got banned.
                 Can be either :class:`User` or :class:`Member` depending on
                 whether the user was in the guild at the time of removal.
    :type user: Union[:class:`User`, :class:`Member`]

.. function:: on_member_unban(guild, user)

    Called when a :class:`User` gets unbanned from a :class:`Guild`.

    This requires :attr:`Intents.moderation` to be enabled.

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

Roles
+++++

.. function:: on_guild_role_create(role)
              on_guild_role_delete(role)

    Called when a :class:`Guild` creates or deletes a :class:`Role`.

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

.. function:: on_raw_message_edit(payload)

    Called when a message is edited. Unlike :func:`on_message_edit`, this is called
    regardless of the state of the internal message cache.

    If the message is found in the message cache,
    it can be accessed via :attr:`RawMessageUpdateEvent.cached_message`. The cached message represents
    the message before it has been edited. For example, if the content of a message is modified and
    triggers the :func:`on_raw_message_edit` coroutine, the :attr:`RawMessageUpdateEvent.cached_message`
    will return a :class:`Message` object that represents the message before the content was modified.

    Due to the inherently raw nature of this event, the data parameter coincides with
    the raw data given by the :ddocs:`gateway <topics/gateway-events#message-update>`.

    Since the data payload can be partial, care must be taken when accessing stuff in the dictionary.
    One example of a common case of partial data is when the ``'content'`` key is inaccessible. This
    denotes an "embed" only edit, which is an edit in which only the embeds are updated by the Discord
    embed server.

    This requires :attr:`Intents.messages` to be enabled.

    :param payload: The raw event payload data.
    :type payload: :class:`RawMessageUpdateEvent`

.. function:: on_raw_message_delete(payload)

    Called when a message is deleted. Unlike :func:`on_message_delete`, this is
    called regardless of the message being in the internal message cache or not.

    If the message is found in the message cache,
    it can be accessed via :attr:`RawMessageDeleteEvent.cached_message`

    This requires :attr:`Intents.messages` to be enabled.

    :param payload: The raw event payload data.
    :type payload: :class:`RawMessageDeleteEvent`

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
    If channel is an :class:`abc.Messageable` instance, it could be a :class:`TextChannel`,
    :class:`VoiceChannel`, :class:`StageChannel`, :class:`GroupChannel`, or :class:`DMChannel`.

    .. versionchanged:: 2.5
        ``channel`` may be a type :class:`ForumChannel`

    .. versionchanged:: 2.9
        ``channel`` may be a type :class:`StageChannel`

    If the ``channel`` is a :class:`TextChannel`, :class:`ForumChannel`, :class:`VoiceChannel`, or :class:`StageChannel` then the
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


Enumerations
------------

Event
~~~~~

.. autoclass:: Event
    :members:
