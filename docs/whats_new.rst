.. currentmodule:: disnake

.. |commands| replace:: [:ref:`ext.commands <discord_ext_commands>`]
.. |tasks| replace:: [:ref:`ext.tasks <discord_ext_tasks>`]

.. _whats_new:

Changelog
============

This page keeps a detailed human friendly rendering of what's new and changed
in specific versions.


.. _vp2p4p0:

v2.4.0
------

This version contains many new features, including attachment options, modals,
and the ability to directly send message components without views,
as well as several fixes and other general improvements.

Breaking Changes
~~~~~~~~~~~~~~~~~

- The constructor of :class:`ApplicationCommand` and its subtypes no longer accepts ``**kwargs`` for setting internal values (:issue:`249`)
    - This shouldn't affect anyone, as ``**kwargs`` was only used for setting fields returned by the API and had no effect if the user set them
- :attr:`Interaction.permissions` now returns proper permission values in DMs (:issue:`321`)
- The ``reason`` parameter for sticker endpoints in :class:`HTTPClient` is now kwarg-only


Deprecations
~~~~~~~~~~~~~

- :attr:`Thread.archiver_id` is not being provided by the API anymore and will be removed in a future version (:issue:`295`)
- :attr:`Invite.revoked` is not being provided by the API anymore and will be removed in a future version (:issue:`309`)


New Features
~~~~~~~~~~~~~

- Add :attr:`Interaction.locale` and :attr:`Interaction.guild_locale` properties to interactions (:issue:`225`)
- Add :class:`ui.ActionRow` and ``components`` kwarg to send methods (:issue:`224`)
- Add :class:`ui.WrappedComponent` as a base class for all UI components (:issue:`253`)
    - :class:`ui.Item` now inherits from :class:`ui.WrappedComponent`. It's no longer a base class for all UI components.
- Implement modals and text inputs (:issue:`253`)
    - Add :class:`TextInput` component.
    - Add :class:`ui.Modal` as a high-level implementation of modals.
    - Add :class:`ui.TextInput` for modals. It inherits from :class:`ui.WrappedComponent` and adds more functionality on top of :class:`TextInput`.
    - Add :meth:`InteractionResponse.send_modal` to support new interaction response type.
    - Add :func:`on_modal_submit` event.
- Add :attr:`MessageFlags.failed_to_mention_roles_in_thread` (:issue:`238`)
- Use logger for application command sync debug (:issue:`230`)
- |commands| Improve application command sync algorithm (:issue:`240`)
- Use HTTP API v9 (:issue:`250`)
- |commands| Add :class:`commands.Range <disnake.ext.commands.Range>`, see :ref:`param_ranges` (:issue:`237`, :issue:`276`, :issue:`316`)
- |commands| Add :func:`Bot.load_extensions <disnake.ext.commands.Bot.load_extensions>` and :func:`utils.search_directory` (:issue:`245`)
- |commands| Add :class:`commands.LargeInt <disnake.ext.commands.LargeInt>` (:issue:`264`)
- Add ``with_message`` parameter to :func:`InteractionResponse.defer` to support deferring component interaction responses with messages (:issue:`248`)
- Add :func:`Widget.edit` (:issue:`266`)
- Add the ability to specify a default color for embeds (:issue:`203`)
- Add :attr:`PartialInviteGuild.nsfw_level` and :attr:`PartialInviteGuild.vanity_url_code` (:issue:`297`)
- Add :attr:`Thread.create_timestamp` (:issue:`285`)
- Add :attr:`Message.thread` (:issue:`291`)
- Add :attr:`Permissions.events` and :attr:`Permissions.private_channel`, improve existing factory methods (:issue:`286`, :issue:`321`)
- Support images in :class:`GuildScheduledEvent` (:issue:`280`)
- Add :attr:`PartyType.sketch_heads` and :attr:`PartyType.ocho` (:issue:`306`)
- Support :class:`Thread` annotations in slash commands (:issue:`305`)
- :attr:`Interaction.bot`, :attr:`Interaction.client`, :attr:`Interaction.channel` and :attr:`Interaction.channel_id` are no longer optional (:issue:`279`)
- Support timeouts in :func:`abc.GuildChannel.permissions_for` and other channel types (:issue:`289`)
- Support :class:`disnake.Attachment` options in slash commands (:issue:`226`)
- Add ``attachments`` parameter to :func:`InteractionResponse.edit_message` (:issue:`335`)
- Add :meth:`Guild.get_or_fetch_members` with an alias :meth:`Guild.getch_members` (:issue:`322`).
- Add :attr:`abc.GuildChannel.jump_url`, :attr:`DMChannel.jump_url` and :attr:`Thread.jump_url` (:issue:`319`)


Bug Fixes
~~~~~~~~~~

- Fix missing support for ``reason`` parameter in some methods (:issue:`266`)
- Improve validation of slash command and option names (:issue:`267`)
- |commands| Fix typing of ``ctx`` parameter in :class:`~disnake.ext.commands.Converter` (:issue:`292`)
- Fix :func:`Guild.get_command` never returning any commands (:issue:`333`)
- Return list of members from :func:`Guild.chunk` (:issue:`334`)
- Fix handling of uppercase slash command names (:issue:`346`)
- Fix ``permissions`` annotation of :func:`abc.GuildChannel.set_permissions` (:issue:`349`)
- Fix :func:`tasks.loop <disnake.ext.tasks.loop>` usage with fixed times (:issue:`337`)


Documentation
~~~~~~~~~~~~~~

- Show tooltips when hovering over links (:issue:`236`, :issue:`242`)
- General content improvements/adjustments (:issue:`275`)
- Slight redesign and general layout improvements (:issue:`278`)


Miscellaneous
~~~~~~~~~~~~~~

- Improve examples (:issue:`209`, :issue:`262`, :issue:`270`, :issue:`307`, :issue:`332`, :issue:`341`)
- Improve typing/annotations of several parts of the library (:issue:`249`, :issue:`256`, :issue:`263`, :issue:`279`, :issue:`292`, :issue:`299`, :issue:`308`)
- Add additional pre-commit hooks for development (:issue:`233`)
- Add taskipy for development (:issue:`234`)
- Improve member deserialization (:issue:`304`)
- Split application command objects into separate types for data returned by the API (:issue:`299`)
- Update README banner (:issue:`343`)


.. _vp2p3p2:

v2.3.2
------

Bug Fixes
~~~~~~~~~

- Fix invalid default value for application command option descriptions (:issue:`338`)


.. _vp2p3p1:

v2.3.1
------

Bug Fixes
~~~~~~~~~

- |commands| Fix Python 3.10 union type annotations in slash commands (:issue:`231`)
- Fix double ``@`` when mentioning default role (:issue:`244`)
- Fix a command sync bug which prevented registering two application commands with the same name but different types (:issue:`254`)
- Fix :func:`GuildScheduledEvent.fetch_users` (:issue:`274`)
- Fix bug when editing a :class:`~ui.View` with URL buttons that resulted in the ``row`` attribute being reset (:issue:`252`)
- |commands| Fix :class:`~ext.commands.MessageConverter` not defaulting to current channel if no channel ID specified (:issue:`284`)
- Fix attachment descriptions not working after recent API change (:issue:`241`)
- Fix incorrect type check in :func:`Guild.create_scheduled_event` using :class:`StagePrivacyLevel` instead of :class:`GuildScheduledEventPrivacyLevel` (:issue:`263`)
- |commands| Fix exceptions that occurred when using a :class:`Union` in a slash command parameter annotation
- |commands| Fix dynamic command cooldowns (:issue:`320`)
- Fix type-checking of ``guild_ids`` / ``test_guilds`` parameters which could break application command caching (:issue:`300`, :issue:`325`)
- Fix :func:`Guild.create_sticker` not working when no description was provided (:issue:`328`)


Documentation
~~~~~~~~~~~~~

- Fix :func:`~ext.commands.guild_permissions` documentation
- Fix missing dropdown icon (:issue:`235`)


Miscellaneous
~~~~~~~~~~~~~

- Add ``isort`` and ``black`` pre-commit hooks, run isort (:issue:`169`, :issue:`173`, :issue:`233`)
- Rename ``tests`` directory (:issue:`232`)


.. _vp2p3p0:

v2.3.0
-------

This version contains several new features and fixes,
notably support for guild scheduled events, guild timeouts,
and a slash command rework with parameter injections, as well as several documentation fixes.

Note: the :ref:`version_guarantees` have been updated to more accurately reflect the versioning scheme this library is following.

Breaking Changes
~~~~~~~~~~~~~~~~~

- The supported aiohttp version range changed from ``>=3.6.0,<3.8.0`` to ``>=3.7.0,<3.9.0``
- Due to the upcoming text-in-voice feature (not yet released at the time of writing),
  many methods/properties that previously returned a :class:`TextChannel` can now also return a :class:`VoiceChannel`, which shares many but not all of its methods.
  Also see the details for text-in-voice under "New Features" below, which include a few important things to note.
- Slash command internals have undergone an extensive rework, and while existing code should still work as before, it is recommended that you do some testing using the new implementation first
- :func:`Bot.get_slash_command <ext.commands.Bot.get_slash_command>` may now also return :class:`SubCommandGroup <ext.commands.SubCommandGroup>` or :class:`SubCommand <ext.commands.SubCommand>` instances, see documentation
- ``disnake.types.ThreadArchiveDuration`` is now ``ThreadArchiveDurationLiteral``, to avoid confusion with the new :class:`ThreadArchiveDuration` enum

Deprecations
~~~~~~~~~~~~~

- The ``role_ids`` and ``user_ids`` parameters for :func:`guild_permissions <ext.commands.guild_permissions>` are now
  ``roles`` and ``users`` respectively; the old parameter names will be removed in a future version

New Features
~~~~~~~~~~~~~

- Add guild scheduled events (:issue:`151`, :issue:`217`)
    - New intent: :attr:`Intents.guild_scheduled_events` (enabled by default)
    - New types
        - :class:`GuildScheduledEvent`
        - :class:`GuildScheduledEventMetadata`
        - :class:`GuildScheduledEventEntityType`
        - :class:`GuildScheduledEventStatus`
        - :class:`GuildScheduledEventPrivacyLevel`
    - Guild additions/changes
        - :attr:`Guild.scheduled_events`
        - :func:`Guild.get_scheduled_event`
        - :func:`Guild.fetch_scheduled_event`
        - :func:`Guild.fetch_scheduled_events`
        - :func:`Guild.create_scheduled_event`
    - Invite additions/changes
        - :attr:`Invite.guild_scheduled_event`
        - ``guild_scheduled_event`` parameter on :func:`abc.GuildChannel.create_invite`
        - ``guild_scheduled_event_id`` parameter on :func:`Client.fetch_invite`
        - Include ``event`` URL parameter in :attr:`Invite.url` if applicable
        - Support parsing scheduled event ID from invite URLs
    - New events
        - :func:`on_guild_scheduled_event_create`
        - :func:`on_guild_scheduled_event_update`
        - :func:`on_guild_scheduled_event_delete`
        - :func:`on_guild_scheduled_event_subscribe` and :func:`on_raw_guild_scheduled_event_subscribe`
        - :func:`on_guild_scheduled_event_unsubscribe` and :func:`on_raw_guild_scheduled_event_unsubscribe`
    - New audit log actions
        - :attr:`AuditLogAction.guild_scheduled_event_create`
        - :attr:`AuditLogAction.guild_scheduled_event_update`
        - :attr:`AuditLogAction.guild_scheduled_event_delete`
- Add guild timeouts (:issue:`161`, :issue:`221`, :issue:`223`)
    - :func:`Guild.timeout`
    - :func:`Member.timeout`
    - :attr:`Member.current_timeout`
    - ``timeout`` parameter on :func:`Member.edit`
    - New permission: :attr:`Permissions.moderate_members`
- Add preliminary support for text-in-voice (:issue:`162`, :issue:`177`)
    - Many methods/properties that previously returned a :class:`TextChannel` can now also return a :class:`VoiceChannel`, which shares many but not all of its methods
    - Important notes:
        - This feature is only available in a very limited number of servers at the time of writing this, and the API is still being developed; therefore, expect changes in the future
        - Text-in-voice currently does **not** support these text channel features (note: this is not guaranteed to be an exhaustive list): threads, webhooks, nsfw flags, slowmode
        - The ``nsfw`` and ``slowmode_delay`` values/parameters are currently not supported by the API and are still TBD
        - Pinned messages are currently not exposed in the client UI, and while the API for them works, their future is uncertain
    - :class:`VoiceChannel` now inherits from :class:`abc.Messageable`
    - New :class:`VoiceChannel` properties:
      :attr:`.nsfw <VoiceChannel.nsfw>`, :attr:`.slowmode_delay <VoiceChannel.slowmode_delay>`, :attr:`.last_message_id <VoiceChannel.last_message_id>`, :attr:`.last_message <VoiceChannel.last_message>`
    - New :class:`VoiceChannel` methods:
      :func:`.is_nsfw <VoiceChannel.is_nsfw>`, :func:`.get_partial_message <VoiceChannel.get_partial_message>`
    - ``nsfw`` and ``slowmode_delay`` parameters for :func:`VoiceChannel.edit`
- |commands| Add parameter injections (`example <https://github.com/DisnakeDev/disnake/blob/master/examples/slash_commands/injections.py>`_) (:issue:`130`)
    - :func:`inject <ext.commands.inject>`
    - :func:`register_injection <ext.commands.register_injection>`
    - :func:`converter_method <ext.commands.converter_method>`

- Add attachment descriptions (see :class:`File`, :class:`Attachment`) (:issue:`100`)
- Add :func:`on_raw_typing` event (:issue:`176`)
- Add :attr:`Guild.approximate_member_count` and :attr:`Guild.approximate_presence_count` (available on manually fetched guilds) (:issue:`139`)
- Add :attr:`Permissions.start_embedded_activities` (:issue:`160`)
- Add :class:`ThreadArchiveDuration` enum, containing the currently valid values for the thread auto-archive feature (:issue:`187`)
- |commands| Add :class:`PermissionsConverter <ext.commands.PermissionsConverter>`, which allows the conversion of a value or a (list of) permission names to a :class:`Permissions` instance
  (using a :class:`Permissions` annotation)
- Add :attr:`AppInfo.flags`
- |commands| Add ``channel_types`` parameter to :func:`Param <ext.commands.Param>`/:class:`ParamInfo <ext.commands.ParamInfo>` (:issue:`130`)
- Add support for setting ``slowmode_delay`` on thread creation (:func:`TextChannel.create_thread`, :func:`Message.create_thread`) (:issue:`132`)
- Add ``invitable`` parameter to :func:`TextChannel.create_thread` (:issue:`132`)
- Add ``fail_if_not_exists`` parameter to :func:`Message.reply` (:issue:`199`, :issue:`211`)
- |commands| :func:`Bot.get_slash_command <ext.commands.Bot.get_slash_command>` now works similar to :func:`Bot.get_command <ext.commands.Bot.get_command>`,
  in that it can also return subcommands/groups for inputs like ``"foo bar"`` (:issue:`149`)
- Add new aliases for :class:`ApplicationCommandInteraction`:
  ``CommandInteraction``, ``CmdInteraction``, ``CommandInter``, ``CmdInter``, ``AppCommandInteraction``

- Add a base class for warnings emitted by this library, :class:`DiscordWarning` (:issue:`118`)
- Add new warnings (emitted instead of just using ``print`` for warnings):
  :class:`ConfigWarning`, :class:`SyncWarning` (:issue:`118`)

- Add new voice channel activities: (:issue:`145`, :issue:`148`, :issue:`183`)
    - :attr:`PartyType.watch_together`
    - :attr:`PartyType.checkers`
    - :attr:`PartyType.spellcast`
    - :attr:`PartyType.awkword`
    - :attr:`PartyType.sketchy_artist`
- Add new flags/enum values: (:issue:`148`, :issue:`194`)
    - :attr:`MessageType.context_menu_command`
    - :attr:`Status.streaming`
    - :attr:`SystemChannelFlags.join_notification_replies`
    - :attr:`MessageFlags.loading`
    - :attr:`UserFlags.http_interactions_bot`, :attr:`PublicUserFlags.http_interactions_bot`
    - :attr:`UserFlags.spammer`, :attr:`PublicUserFlags.spammer`


Bug Fixes
~~~~~~~~~~

- Fix dispatch of typing events in DMs (:issue:`176`)
- Try to retrieve objects in received interactions from cache first (fixing properties like :attr:`Member.status` on member parameters for commands) (:issue:`182`, :issue:`213`)
- Fix return type annotation of :func:`ui.button` and :func:`ui.select` decorators (:issue:`163`)
- Fix incorrect URL returned by :attr:`Template.url`
- Fix sending local files in embeds with interactions/webhooks if only one embed was specified (:issue:`193`)
- Fix leftover uses of ``json``, which didn't use ``orjson`` if available (:issue:`184`)
- Fix :attr:`Message.channel` type being :class:`DMChannel` for ephemeral messages in :func:`on_message` (:issue:`197`)
- Fix command/option name validation (:issue:`210`)
- Always close files after completing HTTP requests (:issue:`124`)
- |commands| Fix unnecessary application command sync without changes
- |commands| Fix incorrect detection of deprecated guild commands in sync algorithm while sync is in progress (:issue:`205`)


Documentation
~~~~~~~~~~~~~~

- Move documentation to https://docs.disnake.dev/
- Update :ref:`version_guarantees` (:issue:`200`)
- Clarify :func:`Interaction.original_message` documentation regarding different response types (:issue:`140`)
- Clarify :func:`Interaction.send` documentation (:issue:`188`)
- Redirect searches for ``color`` to ``colour`` (:issue:`153`)
- Add documentation for new guild feature values (:issue:`148`)
- Add documentation for several methods/properties: (:issue:`153`)
    - :attr:`Client.global_application_commands`
    - :attr:`Client.global_slash_commands`
    - :attr:`Client.global_user_commands`
    - :attr:`Client.global_message_commands`
    - :func:`Bot.on_slash_command_error <ext.commands.Bot.on_slash_command_error>`
    - :func:`Bot.on_user_command_error <ext.commands.Bot.on_user_command_error>`
    - :func:`Bot.on_message_command_error <ext.commands.Bot.on_message_command_error>`
    - :func:`on_slash_command_completion <.ext.commands.on_slash_command_completion>`
    - :func:`on_user_command_completion <.ext.commands.on_user_command_completion>`
    - :func:`on_message_command_completion <.ext.commands.on_message_command_completion>`
    - :attr:`ApplicationCommandInteraction.bot`
    - :class:`InvokableApplicationCommand <ext.commands.InvokableApplicationCommand>`
- Fix incorrect type for :attr:`Invite.channel` in documentation
- Add additional information about application command sync algorithm and syncing commands in sharded bots (:issue:`205`)


Miscellaneous
~~~~~~~~~~~~~~

- Add Python 3.10 to package classifiers (:issue:`127`)
- Change supported aiohttp version range from ``>=3.6.0,<3.8.0`` to ``>=3.7.0,<3.9.0`` (:issue:`119`, :issue:`164`)
- Add guide for configuring inviting a bot through its profile (:issue:`153`)
- Rewrite project README (:issue:`191`)
- Improve examples (:issue:`143`)


.. _vp2p2p3:

v2.2.3
------

Bug Fixes
~~~~~~~~~

- Fix invalid default value for application command option descriptions (:issue:`338`)


.. _vp2p2p2:

v2.2.2
-------

Bug Fixes
~~~~~~~~~~

- Fix channel conversion in audit log entries
- Fix improper error handling in context menu commands
- Supply :attr:`ApplicationCommandInteraction.application_command` in autocomplete callbacks
- Fix :class:`Select.append_option <disnake.ui.Select.append_option>` not raising an error if 25 options have already been added
- Improve check for ``options`` parameter on slash commands and subcommands
- Improve parameter parsing for converters
- Fix warning related to new option properties

Documentation
~~~~~~~~~~~~~~

- Update repository links to new organization
- Fix duplicate entries in documentation
- Fix incorrect ``versionadded`` tags
- Add documentation for :class:`InteractionBot <ext.commands.InteractionBot>` and :class:`AutoShardedInteractionBot <ext.commands.AutoShardedInteractionBot>`

.. _vp2p2p1:

v2.2.1
-------

Bug Fixes
~~~~~~~~~~

- Fixed error related to guild member count

.. _vp2p2p0:

v2.2.0
-------

New Features
~~~~~~~~~~~~~~

- Add :meth:`Interaction.send`
- Add kwarg ``attachments`` to edit methods
- Add kwargs ``file`` and ``files`` to :meth:`InteractionResponse.edit_message`, :meth:`PartialMessage.edit` and :meth:`Message.edit`
- Add kwarg ``file`` to :meth:`Embed.set_image` and :meth:`Embed.set_thumbnail`
- Add kwarg ``delay`` to :meth:`Interaction.delete_original_message` and :meth:`WebhookMessage.delete`
- Add kwarg ``delete_after`` to :meth:`InteractionResponse.send_message` and :meth:`WebhookMessage.send`
- |commands| Add :meth:`InvokableSlashCommand.autocomplete <ext.commands.InvokableSlashCommand.autocomplete>` (alternative method of adding autocomplete functions)
- |commands| Add :meth:`SubCommand.autocomplete <ext.commands.SubCommand.autocomplete>` (alternative method of adding autocomplete functions)
- |commands| Add :meth:`Cog.cog_load <ext.commands.Cog.cog_load>`
- |commands| Error handlers now can cancel each other by returning ``True``

.. _vp2p1p5:

v2.1.5
-------

New Features
~~~~~~~~~~~~~~

- Add :class:`InteractionReference`
- Add :class:`UnresolvedGuildApplicationCommandPermissions`
- Add :attr:`Message.interaction`
- Add kwargs ``min_value`` and ``max_value`` in :class:`Option`
- |commands| Add kwarg ``min_value`` (with aliases ``ge``, ``gt``) to :func:`Param <ext.commands.Param>`
- |commands| Add kwarg ``max_value`` (with aliases ``le``, ``lt``) to :func:`Param <ext.commands.Param>`
- |commands| Add kwarg ``owner`` to :func:`guild_permissions <ext.commands.guild_permissions>`

Bug Fixes
~~~~~~~~~~

- Command deletions on reconnections
- Pending sync tasks on loop termination

.. _vp2p1p4:

v2.1.4
-------

Bug Fixes
~~~~~~~~~~

- Fixed some issues with application command permissions synchronisation

.. _vp2p1p3:

v2.1.3
-------

New Features
~~~~~~~~~~~~~~

- Add :class:`GuildApplicationCommandPermissions`
- Add :class:`PartialGuildApplicationCommandPermissions`
- Add :attr:`ApplicationCommandInteraction.filled_options` property
- Add :func:`on_slash_command_completion <.ext.commands.on_slash_command_completion>`
- Add :func:`on_user_command_completion <.ext.commands.on_user_command_completion>`
- Add :func:`on_message_command_completion <.ext.commands.on_message_command_completion>`
- |commands| Add :class:`AutoShardedInteractionBot <ext.commands.AutoShardedInteractionBot>`
- |commands| Add :class:`InteractionBot <ext.commands.InteractionBot>`
- |commands| Add :func:`guild_permissions <ext.commands.guild_permissions>`
- |commands| Add kwargs ``sync_commands_on_cog_unload`` and ``sync_permissions`` to :class:`InteractionBotBase <ext.commands.InteractionBotBase>`

Bug Fixes
~~~~~~~~~~

- Music
- ``default_permission`` kwarg in user / message commands
- Commands no longer sync during the loop termination

.. _vp2p1p2:

v2.1.2
-------

This is the first stable version of this discord.py 2.0 fork.

New Features
~~~~~~~~~~~~~~

- Add interaction hierarchy. :class:`Interaction` is now the base class for other interaction types, such as :class:`ApplicationCommandInteraction` and :class:`MessageInteraction`.
- Add interaction data wrappers: :class:`ApplicationCommandInteractionData` and :class:`MessageInteractionData`.
- Add interaction data option wrapper: :class:`ApplicationCommandInteractionDataOption`
- Add :meth:`Client.bulk_edit_command_permissions`
- Add :meth:`Client.bulk_overwrite_global_commands`
- Add :meth:`Client.bulk_overwrite_guild_commands`
- Add :meth:`Client.create_global_command`
- Add :meth:`Client.create_guild_command`
- Add :meth:`Client.delete_global_command`
- Add :meth:`Client.delete_guild_command`
- Add :meth:`Client.edit_command_permissions`
- Add :meth:`Client.edit_global_command`
- Add :meth:`Client.edit_guild_command`
- Add :meth:`Client.fetch_command_permissions`
- Add :meth:`Client.fetch_global_commands`
- Add :meth:`Client.fetch_global_command`
- Add :meth:`Client.fetch_guild_commands`
- Add :meth:`Client.fetch_guild_command`
- Add :meth:`Client.get_global_command`
- Add :meth:`Client.get_global_command_named`
- Add :meth:`Client.get_guild_application_commands`
- Add :meth:`Client.get_guild_slash_commands`
- Add :meth:`Client.get_guild_user_commands`
- Add :meth:`Client.get_guild_message_commands`
- Add :meth:`Client.get_guild_command`
- Add :meth:`Client.get_guild_command_named`
- Add :attr:`Client.global_application_commands`
- Add :attr:`Client.global_slash_commands`
- Add :attr:`Client.global_user_commands`
- Add :attr:`Client.global_message_commands`
- |commands| Support for slash commands and context menus.
- |commands| Add :class:`InvokableApplicationCommand <ext.commands.InvokableApplicationCommand>` - the base class for invokable slash commands and context menus.
- |commands| Add :class:`InvokableSlashCommand <ext.commands.InvokableSlashCommand>` for slash command management.
- |commands| Add :class:`SubCommand <ext.commands.SubCommand>` for slash sub-command management.
- |commands| Add :class:`SubCommandGroup <ext.commands.SubCommandGroup>` for slash sub-command group management.
- |commands| Add :class:`InvokableUserCommand <ext.commands.InvokableUserCommand>` for user command management (context menus).
- |commands| Add :class:`InvokableMessageCommand <ext.commands.InvokableMessageCommand>` for message command management (context menus).
- |commands| Add :class:`ParamInfo <ext.commands.ParamInfo>` for wrapping annotations.
- |commands| Add :func:`slash_command <ext.commands.slash_command>` for slash command definitions.
- |commands| Add :func:`user_command <ext.commands.user_command>` for user command definitions (context menus).
- |commands| Add :func:`message_command <ext.commands.message_command>` for message command definitions (context menus).
- |commands| Add :func:`Param <ext.commands.Param>` (with an alias :func:`param <ext.commands.param>`) in case :class:`ParamInfo <ext.commands.ParamInfo>` causes linter errors.
- |commands| Add :meth:`Bot.slash_command <ext.commands.Bot.slash_command>` for slash command definitions.
- |commands| Add :meth:`Bot.user_command <ext.commands.Bot.user_command>` for user command definitions (context menus).
- |commands| Add :meth:`Bot.message_command <ext.commands.Bot.message_command>` for message command definitions (context menus).
- |commands| Add :meth:`Bot.after_slash_command_invoke <ext.commands.Bot.after_slash_command_invoke>` - a decorator for post-invoke hooks for slash commands.
- |commands| Add :meth:`Bot.after_user_command_invoke <ext.commands.Bot.after_user_command_invoke>` - a decorator for post-invoke hooks for user commands.
- |commands| Add :meth:`Bot.after_message_command_invoke <ext.commands.Bot.after_message_command_invoke>` - a decorator for post-invoke hooks for message commands.
- |commands| Add :meth:`Bot.before_slash_command_invoke <ext.commands.Bot.before_slash_command_invoke>` - a decorator for pre-invoke hooks for slash commands.
- |commands| Add :meth:`Bot.before_user_command_invoke <ext.commands.Bot.before_user_command_invoke>` - a decorator for pre-invoke hooks for user commands.
- |commands| Add :meth:`Bot.before_message_command_invoke <ext.commands.Bot.before_message_command_invoke>` - a decorator for pre-invoke hooks for message commands.
- |commands| Add :meth:`Bot.add_slash_command <ext.commands.Bot.add_slash_command>`
- |commands| Add :meth:`Bot.add_user_command <ext.commands.Bot.add_user_command>`
- |commands| Add :meth:`Bot.add_message_command <ext.commands.Bot.add_message_command>`
- |commands| Add :meth:`Bot.remove_slash_command <ext.commands.Bot.remove_slash_command>`
- |commands| Add :meth:`Bot.remove_user_command <ext.commands.Bot.remove_user_command>`
- |commands| Add :meth:`Bot.remove_message_command <ext.commands.Bot.remove_message_command>`
- |commands| Add :meth:`Bot.get_slash_command <ext.commands.Bot.get_slash_command>`
- |commands| Add :meth:`Bot.get_user_command <ext.commands.Bot.get_user_command>`
- |commands| Add :meth:`Bot.get_message_command <ext.commands.Bot.get_message_command>`
- |commands| Add :meth:`Bot.slash_command_check <ext.commands.Bot.slash_command_check>`
- |commands| Add :meth:`Bot.slash_command_check_once <ext.commands.Bot.slash_command_check_once>`
- |commands| Add :meth:`Bot.user_command_check <ext.commands.Bot.user_command_check>`
- |commands| Add :meth:`Bot.user_command_check_once <ext.commands.Bot.user_command_check_once>`
- |commands| Add :meth:`Bot.message_command_check <ext.commands.Bot.message_command_check>`
- |commands| Add :meth:`Bot.message_command_check_once <ext.commands.Bot.message_command_check_once>`
- |commands| Add :meth:`Cog.cog_slash_command_check <ext.commands.Cog.cog_slash_command_check>`
- |commands| Add :meth:`Cog.cog_user_command_check <ext.commands.Cog.cog_user_command_check>`
- |commands| Add :meth:`Cog.cog_message_command_check <ext.commands.Cog.cog_message_command_check>`
- |commands| Add :meth:`Cog.cog_slash_command_error <ext.commands.Cog.cog_slash_command_error>`
- |commands| Add :meth:`Cog.cog_user_command_error <ext.commands.Cog.cog_user_command_error>`
- |commands| Add :meth:`Cog.cog_message_command_error <ext.commands.Cog.cog_message_command_error>`
- |commands| Add :meth:`Cog.cog_before_slash_command_invoke <ext.commands.Cog.cog_before_slash_command_invoke>`
- |commands| Add :meth:`Cog.cog_after_slash_command_invoke <ext.commands.Cog.cog_after_slash_command_invoke>`
- |commands| Add :meth:`Cog.cog_before_user_command_invoke <ext.commands.Cog.cog_before_user_command_invoke>`
- |commands| Add :meth:`Cog.cog_after_user_command_invoke <ext.commands.Cog.cog_after_user_command_invoke>`
- |commands| Add :meth:`Cog.cog_before_message_command_invoke <ext.commands.Cog.cog_before_message_command_invoke>`
- |commands| Add :meth:`Cog.cog_after_message_command_invoke <ext.commands.Cog.cog_after_message_command_invoke>`
- |commands| Add :meth:`Cog.bot_slash_command_check <ext.commands.Cog.bot_slash_command_check>`
- |commands| Add :meth:`Cog.bot_slash_command_check_once <ext.commands.Cog.bot_slash_command_check_once>`
- |commands| Add :meth:`Cog.bot_user_command_check <ext.commands.Cog.bot_user_command_check>`
- |commands| Add :meth:`Cog.bot_user_command_check_once <ext.commands.Cog.bot_user_command_check_once>`
- |commands| Add :meth:`Cog.bot_message_command_check <ext.commands.Cog.bot_message_command_check>`
- |commands| Add :meth:`Cog.bot_message_command_check_once <ext.commands.Cog.bot_message_command_check_once>`

.. _vp1p7p3:

v1.7.3
--------

Bug Fixes
~~~~~~~~~~

- Fix a crash involving guild uploaded stickers
- Fix :meth:`DMChannel.permissions_for` not having :attr:`Permissions.read_messages` set.

.. _vp1p7p2:

v1.7.2
-------

Bug Fixes
~~~~~~~~~~~

- Fix ``fail_if_not_exists`` causing certain message references to not be usable within :meth:`abc.Messageable.send` and :meth:`Message.reply` (:issue-dpy:`6726`)
- Fix :meth:`Guild.chunk` hanging when the user left the guild. (:issue-dpy:`6730`)
- Fix loop sleeping after final iteration rather than before (:issue-dpy:`6744`)

.. _vp1p7p1:

v1.7.1
-------

Bug Fixes
~~~~~~~~~~~

- |commands| Fix :meth:`Cog.has_error_handler <ext.commands.Cog.has_error_handler>` not working as intended.

.. _vp1p7p0:

v1.7.0
--------

This version is mainly for improvements and bug fixes. This is more than likely the last major version in the 1.x series.
Work after this will be spent on v2.0. As a result, **this is the last version to support Python 3.5**.
Likewise, **this is the last version to support user bots**.

Development of v2.0 will have breaking changes and support for newer API features.

New Features
~~~~~~~~~~~~~~

- Add support for stage channels via :class:`StageChannel` (:issue-dpy:`6602`, :issue-dpy:`6608`)
- Add support for :attr:`MessageReference.fail_if_not_exists` (:issue-dpy:`6484`)
    - By default, if the message you're replying to doesn't exist then the API errors out.
      This attribute tells the Discord API that it's okay for that message to be missing.

- Add support for Discord's new permission serialisation scheme.
- Add an easier way to move channels using :meth:`abc.GuildChannel.move`
- Add :attr:`Permissions.use_slash_commands`
- Add :attr:`Permissions.request_to_speak`
- Add support for voice regions in voice channels via :attr:`VoiceChannel.rtc_region` (:issue-dpy:`6606`)
- Add support for :meth:`PartialEmoji.url_as` (:issue-dpy:`6341`)
- Add :attr:`MessageReference.jump_url` (:issue-dpy:`6318`)
- Add :attr:`File.spoiler` (:issue-dpy:`6317`)
- Add support for passing ``roles`` to :meth:`Guild.estimate_pruned_members` (:issue-dpy:`6538`)
- Allow callable class factories to be used in :meth:`abc.Connectable.play` (:issue-dpy:`6478`)
- Add a way to get mutual guilds from the client's cache via :attr:`User.mutual_guilds` (:issue-dpy:`2539`, :issue-dpy:`6444`)
- :meth:`PartialMessage.edit` now returns a full :class:`Message` upon success (:issue-dpy:`6309`)
- Add :attr:`RawMessageUpdateEvent.guild_id` (:issue-dpy:`6489`)
- :class:`AuditLogEntry` is now hashable (:issue-dpy:`6495`)
- :class:`Attachment` is now hashable
- Add :attr:`Attachment.content_type` attribute (:issue-dpy:`6618`)
- Add support for casting :class:`Attachment` to :class:`str` to get the URL.
- Add ``seed`` parameter for :class:`Colour.random` (:issue-dpy:`6562`)
    - This only seeds it for one call. If seeding for multiple calls is desirable, use :func:`random.seed`.

- Add a :func:`utils.remove_markdown` helper function (:issue-dpy:`6573`)
- Add support for passing scopes to :func:`utils.oauth_url` (:issue-dpy:`6568`)
- |commands| Add support for ``rgb`` CSS function as a parameter to :class:`ColourConverter <ext.commands.ColourConverter>` (:issue-dpy:`6374`)
- |commands| Add support for converting :class:`StoreChannel` via :class:`StoreChannelConverter <ext.commands.StoreChannelConverter>` (:issue-dpy:`6603`)
- |commands| Add support for stripping whitespace after the prefix is encountered using the ``strip_after_prefix`` :class:`~ext.commands.Bot` constructor parameter.
- |commands| Add :attr:`Context.invoked_parents <ext.commands.Context.invoked_parents>` to get the aliases a command's parent was invoked with (:issue-dpy:`1874`, :issue-dpy:`6462`)
- |commands| Add a converter for :class:`PartialMessage` under :class:`ext.commands.PartialMessageConverter` (:issue-dpy:`6308`)
- |commands| Add a converter for :class:`Guild` under :class:`ext.commands.GuildConverter` (:issue-dpy:`6016`, :issue-dpy:`6365`)
- |commands| Add :meth:`Command.has_error_handler <ext.commands.Command.has_error_handler>`
    - This is also adds :meth:`Cog.has_error_handler <ext.commands.Cog.has_error_handler>`
- |commands| Allow callable types to act as a bucket key for cooldowns (:issue-dpy:`6563`)
- |commands| Add ``linesep`` keyword argument to :class:`Paginator <ext.commands.Paginator>` (:issue-dpy:`5975`)
- |commands| Allow ``None`` to be passed to :attr:`HelpCommand.verify_checks <ext.commands.HelpCommand.verify_checks>` to only verify in a guild context (:issue-dpy:`2008`, :issue-dpy:`6446`)
- |commands| Allow relative paths when loading extensions via a ``package`` keyword argument (:issue-dpy:`2465`, :issue-dpy:`6445`)

Bug Fixes
~~~~~~~~~~

- Fix mentions not working if ``mention_author`` is passed in :meth:`abc.Messageable.send` without :attr:`Client.allowed_mentions` set (:issue-dpy:`6192`, :issue-dpy:`6458`)
- Fix user created instances of :class:`CustomActivity` triggering an error (:issue-dpy:`4049`)
    - Note that currently, bot users still cannot set a custom activity due to a Discord limitation.
- Fix :exc:`ZeroDivisionError` being raised from :attr:`VoiceClient.average_latency` (:issue-dpy:`6430`, :issue-dpy:`6436`)
- Fix :attr:`User.public_flags` not updating upon edit (:issue-dpy:`6315`)
- Fix :attr:`Message.call` sometimes causing attribute errors (:issue-dpy:`6390`)
- Fix issue resending a file during request retries on newer versions of ``aiohttp`` (:issue-dpy:`6531`)
- Raise an error when ``user_ids`` is empty in :meth:`Guild.query_members`
- Fix ``__str__`` magic method raising when a :class:`Guild` is unavailable.
- Fix potential :exc:`AttributeError` when accessing :attr:`VoiceChannel.members` (:issue-dpy:`6602`)
- :class:`Embed` constructor parameters now implicitly convert to :class:`str` (:issue-dpy:`6574`)
- Ensure ``disnake`` package is only run if executed as a script (:issue-dpy:`6483`)
- |commands| Fix irrelevant commands potentially being unloaded during cog unload due to failure.
- |commands| Fix attribute errors when setting a cog to :class:`~.ext.commands.HelpCommand` (:issue-dpy:`5154`)
- |commands| Fix :attr:`Context.invoked_with <ext.commands.Context.invoked_with>` being improperly reassigned during a :meth:`~ext.commands.Context.reinvoke` (:issue-dpy:`6451`, :issue-dpy:`6462`)
- |commands| Remove duplicates from :meth:`HelpCommand.get_bot_mapping <ext.commands.HelpCommand.get_bot_mapping>` (:issue-dpy:`6316`)
- |commands| Properly handle positional-only parameters in bot command signatures (:issue-dpy:`6431`)
- |commands| Group signatures now properly show up in :attr:`Command.signature <ext.commands.Command.signature>` (:issue-dpy:`6529`, :issue-dpy:`6530`)

Miscellaneous
~~~~~~~~~~~~~~

- User endpoints and all userbot related functionality has been deprecated and will be removed in the next major version of the library.
- :class:`Permission` class methods were updated to match the UI of the Discord client (:issue-dpy:`6476`)
- ``_`` and ``-`` characters are now stripped when making a new cog using the ``disnake`` package (:issue-dpy:`6313`)

.. _vp1p6p0:

v1.6.0
--------

This version comes with support for replies and stickers.

New Features
~~~~~~~~~~~~~~

- An entirely redesigned documentation. This was the cumulation of multiple months of effort.
    - There's now a dark theme, feel free to navigate to the cog on the screen to change your setting, though this should be automatic.
- Add support for :meth:`AppInfo.icon_url_as` and :meth:`AppInfo.cover_image_url_as` (:issue-dpy:`5888`)
- Add :meth:`Colour.random` to get a random colour (:issue-dpy:`6067`)
- Add support for stickers via :class:`Sticker` (:issue-dpy:`5946`)
- Add support for replying via :meth:`Message.reply` (:issue-dpy:`6061`)
    - This also comes with the :attr:`AllowedMentions.replied_user` setting.
    - :meth:`abc.Messageable.send` can now accept a :class:`MessageReference`.
    - :class:`MessageReference` can now be constructed by users.
    - :meth:`Message.to_reference` can now convert a message to a :class:`MessageReference`.
- Add support for getting the replied to resolved message through :attr:`MessageReference.resolved`.
- Add support for role tags.
    - :attr:`Guild.premium_subscriber_role` to get the "Nitro Booster" role (if available).
    - :attr:`Guild.self_role` to get the bot's own role (if available).
    - :attr:`Role.tags` to get the role's tags.
    - :meth:`Role.is_premium_subscriber` to check if a role is the "Nitro Booster" role.
    - :meth:`Role.is_bot_managed` to check if a role is a bot role (i.e. the automatically created role for bots).
    - :meth:`Role.is_integration` to check if a role is role created by an integration.
- Add :meth:`Client.is_ws_ratelimited` to check if the websocket is rate limited.
    - :meth:`ShardInfo.is_ws_ratelimited` is the equivalent for checking a specific shard.
- Add support for chunking an :class:`AsyncIterator` through :meth:`AsyncIterator.chunk` (:issue-dpy:`6100`, :issue-dpy:`6082`)
- Add :attr:`PartialEmoji.created_at` (:issue-dpy:`6128`)
- Add support for editing and deleting webhook sent messages (:issue-dpy:`6058`)
    - This adds :class:`WebhookMessage` as well to power this behaviour.
- Add :class:`PartialMessage` to allow working with a message via channel objects and just a message_id (:issue-dpy:`5905`)
    - This is useful if you don't want to incur an extra API call to fetch the message.
- Add :meth:`Emoji.url_as` (:issue-dpy:`6162`)
- Add support for :attr:`Member.pending` for the membership gating feature.
- Allow ``colour`` parameter to take ``int`` in :meth:`Guild.create_role` (:issue-dpy:`6195`)
- Add support for ``presences`` in :meth:`Guild.query_members` (:issue-dpy:`2354`)
- |commands| Add support for ``description`` keyword argument in :class:`commands.Cog <ext.commands.Cog>` (:issue-dpy:`6028`)
- |tasks| Add support for calling the wrapped coroutine as a function via ``__call__``.


Bug Fixes
~~~~~~~~~~~

- Raise :exc:`DiscordServerError` when reaching 503s repeatedly (:issue-dpy:`6044`)
- Fix :exc:`AttributeError` when :meth:`Client.fetch_template` is called (:issue-dpy:`5986`)
- Fix errors when playing audio and moving to another channel (:issue-dpy:`5953`)
- Fix :exc:`AttributeError` when voice channels disconnect too fast (:issue-dpy:`6039`)
- Fix stale :class:`User` references when the members intent is off.
- Fix :func:`on_user_update` not dispatching in certain cases when a member is not cached but the user somehow is.
- Fix :attr:`Message.author` being overwritten in certain cases during message update.
    - This would previously make it so :attr:`Message.author` is a :class:`User`.
- Fix :exc:`UnboundLocalError` for editing ``public_updates_channel`` in :meth:`Guild.edit` (:issue-dpy:`6093`)
- Fix uninitialised :attr:`CustomActivity.created_at` (:issue-dpy:`6095`)
- |commands| Errors during cog unload no longer stops module cleanup (:issue-dpy:`6113`)
- |commands| Properly cleanup lingering commands when a conflicting alias is found when adding commands (:issue-dpy:`6217`)

Miscellaneous
~~~~~~~~~~~~~~~

- ``ffmpeg`` spawned processes no longer open a window in Windows (:issue-dpy:`6038`)
- Update dependencies to allow the library to work on Python 3.9+ without requiring build tools. (:issue-dpy:`5984`, :issue-dpy:`5970`)
- Fix docstring issue leading to a SyntaxError in 3.9 (:issue-dpy:`6153`)
- Update Windows opus binaries from 1.2.1 to 1.3.1 (:issue-dpy:`6161`)
- Allow :meth:`Guild.create_role` to accept :class:`int` as the ``colour`` parameter (:issue-dpy:`6195`)
- |commands| :class:`MessageConverter <ext.commands.MessageConverter>` regex got updated to support ``www.`` prefixes (:issue-dpy:`6002`)
- |commands| :class:`UserConverter <ext.commands.UserConverter>` now fetches the API if an ID is passed and the user is not cached.
- |commands| :func:`max_concurrency <ext.commands.max_concurrency>` is now called before cooldowns (:issue-dpy:`6172`)

.. _vp1p5p1:

v1.5.1
-------

Bug Fixes
~~~~~~~~~~~

- Fix :func:`utils.escape_markdown` not escaping quotes properly (:issue-dpy:`5897`)
- Fix :class:`Message` not being hashable (:issue-dpy:`5901`, :issue-dpy:`5866`)
- Fix moving channels to the end of the channel list (:issue-dpy:`5923`)
- Fix seemingly strange behaviour in ``__eq__`` for :class:`PermissionOverwrite` (:issue-dpy:`5929`)
- Fix aliases showing up in ``__iter__`` for :class:`Intents` (:issue-dpy:`5945`)
- Fix the bot disconnecting from voice when moving them to another channel (:issue-dpy:`5904`)
- Fix attribute errors when chunking times out sometimes during delayed on_ready dispatching.
- Ensure that the bot's own member is not evicted from the cache (:issue-dpy:`5949`)

Miscellaneous
~~~~~~~~~~~~~~

- Members are now loaded during ``GUILD_MEMBER_UPDATE`` events if :attr:`MemberCacheFlags.joined` is set. (:issue-dpy:`5930`)
- |commands| :class:`MemberConverter <ext.commands.MemberConverter>` now properly lazily fetches members if not available from cache.
    - This is the same as having ``disnake.Member`` as the type-hint.
- :meth:`Guild.chunk` now allows concurrent calls without spamming the gateway with requests.

.. _vp1p5p0:

v1.5.0
--------

This version came with forced breaking changes that Discord is requiring all bots to go through on October 7th. It is highly recommended to read the documentation on intents, :ref:`intents_primer`.

API Changes
~~~~~~~~~~~~~

- Members and presences will no longer be retrieved due to an API change. See :ref:`privileged_intents` for more info.
- As a consequence, fetching offline members is disabled if the members intent is not enabled.

New Features
~~~~~~~~~~~~~~

- Support for gateway intents, passed via ``intents`` in :class:`Client` using :class:`Intents`.
- Add :attr:`VoiceRegion.south_korea` (:issue-dpy:`5233`)
- Add support for ``__eq__`` for :class:`Message` (:issue-dpy:`5789`)
- Add :meth:`Colour.dark_theme` factory method (:issue-dpy:`1584`)
- Add :meth:`AllowedMentions.none` and :meth:`AllowedMentions.all` (:issue-dpy:`5785`)
- Add more concrete exceptions for 500 class errors under :class:`DiscordServerError` (:issue-dpy:`5797`)
- Implement :class:`VoiceProtocol` to better intersect the voice flow.
- Add :meth:`Guild.chunk` to fully chunk a guild.
- Add :class:`MemberCacheFlags` to better control member cache. See :ref:`intents_member_cache` for more info.
- Add support for :attr:`ActivityType.competing` (:issue-dpy:`5823`)
    - This seems currently unused API wise.

- Add support for message references, :attr:`Message.reference` (:issue-dpy:`5754`, :issue-dpy:`5832`)
- Add alias for :class:`ColourConverter` under ``ColorConverter`` (:issue-dpy:`5773`)
- Add alias for :attr:`PublicUserFlags.verified_bot_developer` under :attr:`PublicUserFlags.early_verified_bot_developer` (:issue-dpy:`5849`)
- |commands| Add support for ``require_var_positional`` for :class:`Command` (:issue-dpy:`5793`)

Bug Fixes
~~~~~~~~~~

- Fix issue with :meth:`Guild.by_category` not showing certain channels.
- Fix :attr:`abc.GuildChannel.permissions_synced` always being ``False`` (:issue-dpy:`5772`)
- Fix handling of cloudflare bans on webhook related requests (:issue-dpy:`5221`)
- Fix cases where a keep-alive thread would ack despite already dying (:issue-dpy:`5800`)
- Fix cases where a :class:`Member` reference would be stale when cache is disabled in message events (:issue-dpy:`5819`)
- Fix ``allowed_mentions`` not being sent when sending a single file (:issue-dpy:`5835`)
- Fix ``overwrites`` being ignored in :meth:`abc.GuildChannel.edit` if ``{}`` is passed (:issue-dpy:`5756`, :issue-dpy:`5757`)
- |commands| Fix exceptions being raised improperly in command invoke hooks (:issue-dpy:`5799`)
- |commands| Fix commands not being properly ejected during errors in a cog injection (:issue-dpy:`5804`)
- |commands| Fix cooldown timing ignoring edited timestamps.
- |tasks| Fix tasks extending the next iteration on handled exceptions (:issue-dpy:`5762`, :issue-dpy:`5763`)

Miscellaneous
~~~~~~~~~~~~~~~

- Webhook requests are now logged (:issue-dpy:`5798`)
- Remove caching layer from :attr:`AutoShardedClient.shards`. This was causing issues if queried before launching shards.
- Gateway rate limits are now handled.
- Warnings logged due to missed caches are now changed to DEBUG log level.
- Some strings are now explicitly interned to reduce memory usage.
- Usage of namedtuples has been reduced to avoid potential breaking changes in the future (:issue-dpy:`5834`)
- |commands| All :class:`BadArgument` exceptions from the built-in converters now raise concrete exceptions to better tell them apart (:issue-dpy:`5748`)
- |tasks| Lazily fetch the event loop to prevent surprises when changing event loop policy (:issue-dpy:`5808`)

.. _vp1p4p2:

v1.4.2
--------

This is a maintenance release with backports from :ref:`vp1p5p0`.

Bug Fixes
~~~~~~~~~~~

- Fix issue with :meth:`Guild.by_category` not showing certain channels.
- Fix :attr:`abc.GuildChannel.permissions_synced` always being ``False`` (:issue-dpy:`5772`)
- Fix handling of cloudflare bans on webhook related requests (:issue-dpy:`5221`)
- Fix cases where a keep-alive thread would ack despite already dying (:issue-dpy:`5800`)
- Fix cases where a :class:`Member` reference would be stale when cache is disabled in message events (:issue-dpy:`5819`)
- Fix ``allowed_mentions`` not being sent when sending a single file (:issue-dpy:`5835`)
- Fix ``overwrites`` being ignored in :meth:`abc.GuildChannel.edit` if ``{}`` is passed (:issue-dpy:`5756`, :issue-dpy:`5757`)
- |commands| Fix exceptions being raised improperly in command invoke hooks (:issue-dpy:`5799`)
- |commands| Fix commands not being properly ejected during errors in a cog injection (:issue-dpy:`5804`)
- |commands| Fix cooldown timing ignoring edited timestamps.
- |tasks| Fix tasks extending the next iteration on handled exceptions (:issue-dpy:`5762`, :issue-dpy:`5763`)

Miscellaneous
~~~~~~~~~~~~~~~

- Remove caching layer from :attr:`AutoShardedClient.shards`. This was causing issues if queried before launching shards.
- |tasks| Lazily fetch the event loop to prevent surprises when changing event loop policy (:issue-dpy:`5808`)

.. _vp1p4p1:

v1.4.1
--------

Bug Fixes
~~~~~~~~~~~

- Properly terminate the connection when :meth:`Client.close` is called (:issue-dpy:`5207`)
- Fix error being raised when clearing embed author or image when it was already cleared (:issue-dpy:`5210`, :issue-dpy:`5212`)
- Fix ``__path__`` to allow editable extensions (:issue-dpy:`5213`)

.. _vp1p4p0:

v1.4.0
--------

Another version with a long development time. Features like Intents are slated to be released in a v1.5 release. Thank you for your patience!

New Features
~~~~~~~~~~~~~~

- Add support for :class:`AllowedMentions` to have more control over what gets mentioned.
    - This can be set globally through :attr:`Client.allowed_mentions`
    - This can also be set on a per message basis via :meth:`abc.Messageable.send`

- :class:`AutoShardedClient` has been completely redesigned from the ground up to better suit multi-process clusters (:issue-dpy:`2654`)
    - Add :class:`ShardInfo` which allows fetching specific information about a shard.
    - The :class:`ShardInfo` allows for reconnecting and disconnecting of a specific shard as well.
    - Add :meth:`AutoShardedClient.get_shard` and :attr:`AutoShardedClient.shards` to get information about shards.
    - Rework the entire connection flow to better facilitate the ``IDENTIFY`` rate limits.
    - Add a hook :meth:`Client.before_identify_hook` to have better control over what happens before an ``IDENTIFY`` is done.
    - Add more shard related events such as :func:`on_shard_connect`, :func:`on_shard_disconnect` and :func:`on_shard_resumed`.

- Add support for guild templates (:issue-dpy:`2652`)
    - This adds :class:`Template` to read a template's information.
    - :meth:`Client.fetch_template` can be used to fetch a template's information from the API.
    - :meth:`Client.create_guild` can now take an optional template to base the creation from.
    - Note that fetching a guild's template is currently restricted for bot accounts.

- Add support for guild integrations (:issue-dpy:`2051`, :issue-dpy:`1083`)
    - :class:`Integration` is used to read integration information.
    - :class:`IntegrationAccount` is used to read integration account information.
    - :meth:`Guild.integrations` will fetch all integrations in a guild.
    - :meth:`Guild.create_integration` will create an integration.
    - :meth:`Integration.edit` will edit an existing integration.
    - :meth:`Integration.delete` will delete an integration.
    - :meth:`Integration.sync` will sync an integration.
    - There is currently no support in the audit log for this.

- Add an alias for :attr:`VerificationLevel.extreme` under :attr:`VerificationLevel.very_high` (:issue-dpy:`2650`)
- Add various grey to gray aliases for :class:`Colour` (:issue-dpy:`5130`)
- Added :attr:`VoiceClient.latency` and :attr:`VoiceClient.average_latency` (:issue-dpy:`2535`)
- Add ``use_cached`` and ``spoiler`` parameters to :meth:`Attachment.to_file` (:issue-dpy:`2577`, :issue-dpy:`4095`)
- Add ``position`` parameter support to :meth:`Guild.create_category` (:issue-dpy:`2623`)
- Allow passing ``int`` for the colour in :meth:`Role.edit` (:issue-dpy:`4057`)
- Add :meth:`Embed.remove_author` to clear author information from an embed (:issue-dpy:`4068`)
- Add the ability to clear images and thumbnails in embeds using :attr:`Embed.Empty` (:issue-dpy:`4053`)
- Add :attr:`Guild.max_video_channel_users` (:issue-dpy:`4120`)
- Add :attr:`Guild.public_updates_channel` (:issue-dpy:`4120`)
- Add ``guild_ready_timeout`` parameter to :class:`Client` and subclasses to control timeouts when the ``GUILD_CREATE`` stream takes too long (:issue-dpy:`4112`)
- Add support for public user flags via :attr:`User.public_flags` and :class:`PublicUserFlags` (:issue-dpy:`3999`)
- Allow changing of channel types via :meth:`TextChannel.edit` to and from a news channel (:issue-dpy:`4121`)
- Add :meth:`Guild.edit_role_positions` to bulk edit role positions in a single API call (:issue-dpy:`2501`, :issue-dpy:`2143`)
- Add :meth:`Guild.change_voice_state` to change your voice state in a guild (:issue-dpy:`5088`)
- Add :meth:`PartialInviteGuild.is_icon_animated` for checking if the invite guild has animated icon (:issue-dpy:`4180`, :issue-dpy:`4181`)
- Add :meth:`PartialInviteGuild.icon_url_as` now supports ``static_format`` for consistency (:issue-dpy:`4180`, :issue-dpy:`4181`)
- Add support for ``user_ids`` in :meth:`Guild.query_members`
- Add support for pruning members by roles in :meth:`Guild.prune_members` (:issue-dpy:`4043`)
- |commands| Implement :func:`~ext.commands.before_invoke` and :func:`~ext.commands.after_invoke` decorators (:issue-dpy:`1986`, :issue-dpy:`2502`)
- |commands| Add a way to retrieve ``retry_after`` from a cooldown in a command via :meth:`Command.get_cooldown_retry_after <.ext.commands.Command.get_cooldown_retry_after>` (:issue-dpy:`5195`)
- |commands| Add a way to dynamically add and remove checks from a :class:`HelpCommand <.ext.commands.HelpCommand>` (:issue-dpy:`5197`)
- |tasks| Add :meth:`Loop.is_running <.ext.tasks.Loop.is_running>` method to the task objects (:issue-dpy:`2540`)
- |tasks| Allow usage of custom error handlers similar to the command extensions to tasks using :meth:`Loop.error <.ext.tasks.Loop.error>` decorator (:issue-dpy:`2621`)


Bug Fixes
~~~~~~~~~~~~

- Fix issue with :attr:`PartialEmoji.url` reads leading to a failure (:issue-dpy:`4015`, :issue-dpy:`4016`)
- Allow :meth:`abc.Messageable.history` to take a limit of ``1`` even if ``around`` is passed (:issue-dpy:`4019`)
- Fix :attr:`Guild.member_count` not updating in certain cases when a member has left the guild (:issue-dpy:`4021`)
- Fix the type of :attr:`Object.id` not being validated. For backwards compatibility ``str`` is still allowed but is converted to ``int`` (:issue-dpy:`4002`)
- Fix :meth:`Guild.edit` not allowing editing of notification settings (:issue-dpy:`4074`, :issue-dpy:`4047`)
- Fix crash when the guild widget contains channels that aren't in the payload (:issue-dpy:`4114`, :issue-dpy:`4115`)
- Close ffmpeg stdin handling from spawned processes with :class:`FFmpegOpusAudio` and :class:`FFmpegPCMAudio` (:issue-dpy:`4036`)
- Fix :func:`utils.escape_markdown` not escaping masked links (:issue-dpy:`4206`, :issue-dpy:`4207`)
- Fix reconnect loop due to failed handshake on region change (:issue-dpy:`4210`, :issue-dpy:`3996`)
- Fix :meth:`Guild.by_category` not returning empty categories (:issue-dpy:`4186`)
- Fix certain JPEG images not being identified as JPEG (:issue-dpy:`5143`)
- Fix a crash when an incomplete guild object is used when fetching reaction information (:issue-dpy:`5181`)
- Fix a timeout issue when fetching members using :meth:`Guild.query_members`
- Fix an issue with domain resolution in voice (:issue-dpy:`5188`, :issue-dpy:`5191`)
- Fix an issue where :attr:`PartialEmoji.id` could be a string (:issue-dpy:`4153`, :issue-dpy:`4152`)
- Fix regression where :attr:`Member.activities` would not clear.
- |commands| A :exc:`TypeError` is now raised when :obj:`typing.Optional` is used within :data:`commands.Greedy <.ext.commands.Greedy>` (:issue-dpy:`2253`, :issue-dpy:`5068`)
- |commands| :meth:`Bot.walk_commands <.ext.commands.Bot.walk_commands>` no longer yields duplicate commands due to aliases (:issue-dpy:`2591`)
- |commands| Fix regex characters not being escaped in :attr:`HelpCommand.clean_prefix <.ext.commands.HelpCommand.clean_prefix>` (:issue-dpy:`4058`, :issue-dpy:`4071`)
- |commands| Fix :meth:`Bot.get_command <.ext.commands.Bot.get_command>` from raising errors when a name only has whitespace (:issue-dpy:`5124`)
- |commands| Fix issue with :attr:`Context.subcommand_passed <.ext.commands.Context.subcommand_passed>` not functioning as expected (:issue-dpy:`5198`)
- |tasks| Task objects are no longer stored globally so two class instances can now start two separate tasks (:issue-dpy:`2294`)
- |tasks| Allow cancelling the loop within :meth:`before_loop <.ext.tasks.Loop.before_loop>` (:issue-dpy:`4082`)


Miscellaneous
~~~~~~~~~~~~~~~

- The :attr:`Member.roles` cache introduced in v1.3 was reverted due to issues caused (:issue-dpy:`4087`, :issue-dpy:`4157`)
- :class:`Webhook` objects are now comparable and hashable (:issue-dpy:`4182`)
- Some more API requests got a ``reason`` parameter for audit logs (:issue-dpy:`5086`)
    - :meth:`TextChannel.follow`
    - :meth:`Message.pin` and :meth:`Message.unpin`
    - :meth:`Webhook.delete` and :meth:`Webhook.edit`

- For performance reasons ``websockets`` has been dropped in favour of ``aiohttp.ws``.
- The blocking logging message now shows the stack trace of where the main thread was blocking
- The domain name was changed from ``discordapp.com`` to ``discord.com`` to prepare for the required domain migration
- Reduce memory usage when reconnecting due to stale references being held by the message cache (:issue-dpy:`5133`)
- Optimize :meth:`abc.GuildChannel.permissions_for` by not creating as many temporary objects (20-32% savings).
- |commands| Raise :exc:`~ext.commands.CommandRegistrationError` instead of :exc:`ClientException` when a duplicate error is registered (:issue-dpy:`4217`)
- |tasks| No longer handle :exc:`HTTPException` by default in the task reconnect loop (:issue-dpy:`5193`)

.. _vp1p3p4:

v1.3.4
--------

Bug Fixes
~~~~~~~~~~~

- Fix an issue with channel overwrites causing multiple issues including crashes (:issue-dpy:`5109`)

.. _vp1p3p3:

v1.3.3
--------

Bug Fixes
~~~~~~~~~~~~

- Change default WS close to 4000 instead of 1000.
    - The previous close code caused sessions to be invalidated at a higher frequency than desired.

- Fix ``None`` appearing in ``Member.activities``. (:issue-dpy:`2619`)

.. _vp1p3p2:

v1.3.2
---------

Another minor bug fix release.

Bug Fixes
~~~~~~~~~~~

- Higher the wait time during the ``GUILD_CREATE`` stream before ``on_ready`` is fired for :class:`AutoShardedClient`.
- :func:`on_voice_state_update` now uses the inner ``member`` payload which should make it more reliable.
- Fix various Cloudflare handling errors (:issue-dpy:`2572`, :issue-dpy:`2544`)
- Fix crashes if :attr:`Message.guild` is :class:`Object` instead of :class:`Guild`.
- Fix :meth:`Webhook.send` returning an empty string instead of ``None`` when ``wait=False``.
- Fix invalid format specifier in webhook state (:issue-dpy:`2570`)
- |commands| Passing invalid permissions to permission related checks now raises ``TypeError``.

.. _vp1p3p1:

v1.3.1
--------

Minor bug fix release.

Bug Fixes
~~~~~~~~~~~

- Fix fetching invites in guilds that the user is not in.
- Fix the channel returned from :meth:`Client.fetch_channel` raising when sending messages. (:issue-dpy:`2531`)

Miscellaneous
~~~~~~~~~~~~~~

- Fix compatibility warnings when using the Python 3.9 alpha.
- Change the unknown event logging from WARNING to DEBUG to reduce noise.

.. _vp1p3p0:

v1.3.0
--------

This version comes with a lot of bug fixes and new features. It's been in development for a lot longer than was anticipated!

New Features
~~~~~~~~~~~~~~

- Add :meth:`Guild.fetch_members` to fetch members from the HTTP API. (:issue-dpy:`2204`)
- Add :meth:`Guild.fetch_roles` to fetch roles from the HTTP API. (:issue-dpy:`2208`)
- Add support for teams via :class:`Team` when fetching with :meth:`Client.application_info`. (:issue-dpy:`2239`)
- Add support for suppressing embeds via :meth:`Message.edit`
- Add support for guild subscriptions. See the :class:`Client` documentation for more details.
- Add :attr:`VoiceChannel.voice_states` to get voice states without relying on member cache.
- Add :meth:`Guild.query_members` to request members from the gateway.
- Add :class:`FFmpegOpusAudio` and other voice improvements. (:issue-dpy:`2258`)
- Add :attr:`RawMessageUpdateEvent.channel_id` for retrieving channel IDs during raw message updates. (:issue-dpy:`2301`)
- Add :attr:`RawReactionActionEvent.event_type` to disambiguate between reaction addition and removal in reaction events.
- Add :attr:`abc.GuildChannel.permissions_synced` to query whether permissions are synced with the category. (:issue-dpy:`2300`, :issue-dpy:`2324`)
- Add :attr:`MessageType.channel_follow_add` message type for announcement channels being followed. (:issue-dpy:`2314`)
- Add :meth:`Message.is_system` to allow for quickly filtering through system messages.
- Add :attr:`VoiceState.self_stream` to indicate whether someone is streaming via Go Live. (:issue-dpy:`2343`)
- Add :meth:`Emoji.is_usable` to check if the client user can use an emoji. (:issue-dpy:`2349`)
- Add :attr:`VoiceRegion.europe` and :attr:`VoiceRegion.dubai`. (:issue-dpy:`2358`, :issue-dpy:`2490`)
- Add :meth:`TextChannel.follow` to follow a news channel. (:issue-dpy:`2367`)
- Add :attr:`Permissions.view_guild_insights` permission. (:issue-dpy:`2415`)
- Add support for new audit log types. See :ref:`discord-api-audit-logs` for more information. (:issue-dpy:`2427`)
    - Note that integration support is not finalized.

- Add :attr:`Webhook.type` to query the type of webhook (:class:`WebhookType`). (:issue-dpy:`2441`)
- Allow bulk editing of channel overwrites through :meth:`abc.GuildChannel.edit`. (:issue-dpy:`2198`)
- Add :class:`Activity.created_at` to see when an activity was started. (:issue-dpy:`2446`)
- Add support for ``xsalsa20_poly1305_lite`` encryption mode for voice. (:issue-dpy:`2463`)
- Add :attr:`RawReactionActionEvent.member` to get the member who did the reaction. (:issue-dpy:`2443`)
- Add support for new YouTube streaming via :attr:`Streaming.platform` and :attr:`Streaming.game`. (:issue-dpy:`2445`)
- Add :attr:`Guild.discovery_splash_url` to get the discovery splash image asset. (:issue-dpy:`2482`)
- Add :attr:`Guild.rules_channel` to get the rules channel of public guilds. (:issue-dpy:`2482`)
    - It should be noted that this feature is restricted to those who are either in Server Discovery or planning to be there.

- Add support for message flags via :attr:`Message.flags` and :class:`MessageFlags`. (:issue-dpy:`2433`)
- Add :attr:`User.system` and :attr:`Profile.system` to know whether a user is an official Discord Trust and Safety account.
- Add :attr:`Profile.team_user` to check whether a user is a member of a team.
- Add :meth:`Attachment.to_file` to easily convert attachments to :class:`File` for sending.
- Add certain aliases to :class:`Permissions` to match the UI better. (:issue-dpy:`2496`)
    - :attr:`Permissions.manage_permissions`
    - :attr:`Permissions.view_channel`
    - :attr:`Permissions.use_external_emojis`

- Add support for passing keyword arguments when creating :class:`Permissions`.
- Add support for custom activities via :class:`CustomActivity`. (:issue-dpy:`2400`)
    - Note that as of now, bots cannot send custom activities yet.

- Add support for :func:`on_invite_create` and :func:`on_invite_delete` events.
- Add support for clearing a specific reaction emoji from a message.
    - :meth:`Message.clear_reaction` and :meth:`Reaction.clear` methods.
    - :func:`on_raw_reaction_clear_emoji` and :func:`on_reaction_clear_emoji` events.

- Add :func:`utils.sleep_until` helper to sleep until a specific datetime. (:issue-dpy:`2517`, :issue-dpy:`2519`)
- |commands| Add support for teams and :attr:`Bot.owner_ids <.ext.commands.Bot.owner_ids>` to have multiple bot owners. (:issue-dpy:`2239`)
- |commands| Add new :attr:`BucketType.role <.ext.commands.BucketType.role>` bucket type. (:issue-dpy:`2201`)
- |commands| Expose :attr:`Command.cog <.ext.commands.Command.cog>` property publicly. (:issue-dpy:`2360`)
- |commands| Add non-decorator interface for adding checks to commands via :meth:`Command.add_check <.ext.commands.Command.add_check>` and :meth:`Command.remove_check <.ext.commands.Command.remove_check>`. (:issue-dpy:`2411`)
- |commands| Add :func:`has_guild_permissions <.ext.commands.has_guild_permissions>` check. (:issue-dpy:`2460`)
- |commands| Add :func:`bot_has_guild_permissions <.ext.commands.bot_has_guild_permissions>` check. (:issue-dpy:`2460`)
- |commands| Add ``predicate`` attribute to checks decorated with :func:`~.ext.commands.check`.
- |commands| Add :func:`~.ext.commands.check_any` check to logical OR multiple checks.
- |commands| Add :func:`~.ext.commands.max_concurrency` to allow only a certain amount of users to use a command concurrently before waiting or erroring.
- |commands| Add support for calling a :class:`~.ext.commands.Command` as a regular function.
- |tasks| :meth:`Loop.add_exception_type <.ext.tasks.Loop.add_exception_type>` now allows multiple exceptions to be set. (:issue-dpy:`2333`)
- |tasks| Add :attr:`Loop.next_iteration <.ext.tasks.Loop.next_iteration>` property. (:issue-dpy:`2305`)

Bug Fixes
~~~~~~~~~~

- Fix issue with permission resolution sometimes failing for guilds with no owner.
- Tokens are now stripped upon use. (:issue-dpy:`2135`)
- Passing in a ``name`` is no longer required for :meth:`Emoji.edit`. (:issue-dpy:`2368`)
- Fix issue with webhooks not re-raising after retries have run out. (:issue-dpy:`2272`, :issue-dpy:`2380`)
- Fix mismatch in URL handling in :func:`utils.escape_markdown`. (:issue-dpy:`2420`)
- Fix issue with ports being read in little endian when they should be big endian in voice connections. (:issue-dpy:`2470`)
- Fix :meth:`Member.mentioned_in` not taking into consideration the message's guild.
- Fix bug with moving channels when there are gaps in positions due to channel deletion and creation.
- Fix :func:`on_shard_ready` not triggering when ``fetch_offline_members`` is disabled. (:issue-dpy:`2504`)
- Fix issue with large sharded bots taking too long to actually dispatch :func:`on_ready`.
- Fix issue with fetching group DM based invites in :meth:`Client.fetch_invite`.
- Fix out of order files being sent in webhooks when there are 10 files.
- |commands| Extensions that fail internally due to ImportError will no longer raise :exc:`~.ext.commands.ExtensionNotFound`. (:issue-dpy:`2244`, :issue-dpy:`2275`, :issue-dpy:`2291`)
- |commands| Updating the :attr:`Paginator.suffix <.ext.commands.Paginator.suffix>` will not cause out of date calculations. (:issue-dpy:`2251`)
- |commands| Allow converters from custom extension packages. (:issue-dpy:`2369`, :issue-dpy:`2374`)
- |commands| Fix issue with paginator prefix being ``None`` causing empty pages. (:issue-dpy:`2471`)
- |commands| :class:`~.commands.Greedy` now ignores parsing errors rather than propagating them.
- |commands| :meth:`Command.can_run <.ext.commands.Command.can_run>` now checks whether a command is disabled.
- |commands| :attr:`HelpCommand.clean_prefix <.ext.commands.HelpCommand.clean_prefix>` now takes into consideration nickname mentions. (:issue-dpy:`2489`)
- |commands| :meth:`Context.send_help <.ext.commands.Context.send_help>` now properly propagates to the :meth:`HelpCommand.on_help_command_error <.ext.commands.HelpCommand.on_help_command_error>` handler.

Miscellaneous
~~~~~~~~~~~~~~~

- The library now fully supports Python 3.8 without warnings.
- Bump the dependency of ``websockets`` to 8.0 for those who can use it. (:issue-dpy:`2453`)
- Due to Discord providing :class:`Member` data in mentions, users will now be upgraded to :class:`Member` more often if mentioned.
- :func:`utils.escape_markdown` now properly escapes new quote markdown.
- The message cache can now be disabled by passing ``None`` to ``max_messages`` in :class:`Client`.
- The default message cache size has changed from 5000 to 1000 to accommodate small bots.
- Lower memory usage by only creating certain objects as needed in :class:`Role`.
- There is now a sleep of 5 seconds before re-IDENTIFYing during a reconnect to prevent long loops of session invalidation.
- The rate limiting code now uses millisecond precision to have more granular rate limit handling.
    - Along with that, the rate limiting code now uses Discord's response to wait. If you need to use the system clock again for whatever reason, consider passing ``assume_synced_clock`` in :class:`Client`.

- The performance of :attr:`Guild.default_role` has been improved from O(N) to O(1). (:issue-dpy:`2375`)
- The performance of :attr:`Member.roles` has improved due to usage of caching to avoid surprising performance traps.
- The GC is manually triggered during things that cause large deallocations (such as guild removal) to prevent memory fragmentation.
- There have been many changes to the documentation for fixes both for usability, correctness, and to fix some linter errors. Thanks to everyone who contributed to those.
- The loading of the opus module has been delayed which would make the result of :func:`opus.is_loaded` somewhat surprising.
- |commands| Usernames prefixed with @ inside DMs will properly convert using the :class:`User` converter. (:issue-dpy:`2498`)
- |tasks| The task sleeping time will now take into consideration the amount of time the task body has taken before sleeping. (:issue-dpy:`2516`)

.. _vp1p2p5:

v1.2.5
--------

Bug Fixes
~~~~~~~~~~~

- Fix a bug that caused crashes due to missing ``animated`` field in Emoji structures in reactions.

.. _vp1p2p4:

v1.2.4
--------

Bug Fixes
~~~~~~~~~~~

- Fix a regression when :attr:`Message.channel` would be ``None``.
- Fix a regression where :attr:`Message.edited_at` would not update during edits.
- Fix a crash that would trigger during message updates (:issue-dpy:`2265`, :issue-dpy:`2287`).
- Fix a bug when :meth:`VoiceChannel.connect` would not return (:issue-dpy:`2274`, :issue-dpy:`2372`, :issue-dpy:`2373`, :issue-dpy:`2377`).
- Fix a crash relating to token-less webhooks (:issue-dpy:`2364`).
- Fix issue where :attr:`Guild.premium_subscription_count` would be ``None`` due to a Discord bug. (:issue-dpy:`2331`, :issue-dpy:`2376`).

.. _vp1p2p3:

v1.2.3
--------

Bug Fixes
~~~~~~~~~~~

- Fix an AttributeError when accessing :attr:`Member.premium_since` in :func:`on_member_update`. (:issue-dpy:`2213`)
- Handle :exc:`asyncio.CancelledError` in :meth:`abc.Messageable.typing` context manager. (:issue-dpy:`2218`)
- Raise the max encoder bitrate to 512kbps to account for nitro boosting. (:issue-dpy:`2232`)
- Properly propagate exceptions in :meth:`Client.run`. (:issue-dpy:`2237`)
- |commands| Ensure cooldowns are properly copied when used in cog level ``command_attrs``.

.. _vp1p2p2:

v1.2.2
--------

Bug Fixes
~~~~~~~~~~~

- Audit log related attribute access have been fixed to not error out when they shouldn't have.

.. _vp1p2p1:

v1.2.1
--------

Bug Fixes
~~~~~~~~~~~

- :attr:`User.avatar_url` and related attributes no longer raise an error.
- More compatibility shims with the ``enum.Enum`` code.

.. _vp1p2p0:

v1.2.0
--------

This update mainly brings performance improvements and various nitro boosting attributes (referred to in the API as "premium guilds").

New Features
~~~~~~~~~~~~~~

- Add :attr:`Guild.premium_tier` to query the guild's current nitro boost level.
- Add :attr:`Guild.emoji_limit`, :attr:`Guild.bitrate_limit`, :attr:`Guild.filesize_limit` to query the new limits of a guild when taking into consideration boosting.
- Add :attr:`Guild.premium_subscription_count` to query how many members are boosting a guild.
- Add :attr:`Member.premium_since` to query since when a member has boosted a guild.
- Add :attr:`Guild.premium_subscribers` to query all the members currently boosting the guild.
- Add :attr:`Guild.system_channel_flags` to query the settings for a guild's :attr:`Guild.system_channel`.
    - This includes a new type named :class:`SystemChannelFlags`
- Add :attr:`Emoji.available` to query if an emoji can be used (within the guild or otherwise).
- Add support for animated icons in :meth:`Guild.icon_url_as` and :attr:`Guild.icon_url`.
- Add :meth:`Guild.is_icon_animated`.
- Add support for the various new :class:`MessageType` involving nitro boosting.
- Add :attr:`VoiceRegion.india`. (:issue-dpy:`2145`)
- Add :meth:`Embed.insert_field_at`. (:issue-dpy:`2178`)
- Add a ``type`` attribute for all channels to their appropriate :class:`ChannelType`. (:issue-dpy:`2185`)
- Add :meth:`Client.fetch_channel` to fetch a channel by ID via HTTP. (:issue-dpy:`2169`)
- Add :meth:`Guild.fetch_channels` to fetch all channels via HTTP. (:issue-dpy:`2169`)
- |tasks| Add :meth:`Loop.stop <.ext.tasks.Loop.stop>` to gracefully stop a task rather than cancelling.
- |tasks| Add :meth:`Loop.failed <.ext.tasks.Loop.failed>` to query if a task had failed somehow.
- |tasks| Add :meth:`Loop.change_interval <.ext.tasks.Loop.change_interval>` to change the sleep interval at runtime (:issue-dpy:`2158`, :issue-dpy:`2162`)

Bug Fixes
~~~~~~~~~~~

- Fix internal error when using :meth:`Guild.prune_members`.
- |commands| Fix :attr:`.Command.invoked_subcommand` being invalid in many cases.
- |tasks| Reset iteration count when the loop terminates and is restarted.
- |tasks| The decorator interface now works as expected when stacking (:issue-dpy:`2154`)

Miscellaneous
~~~~~~~~~~~~~~~

- Improve performance of all Enum related code significantly.
    - This was done by replacing the ``enum.Enum`` code with an API compatible one.
    - This should not be a breaking change for most users due to duck-typing.
- Improve performance of message creation by about 1.5x.
- Improve performance of message editing by about 1.5-4x depending on payload size.
- Improve performance of attribute access on :class:`Member` about by 2x.
- Improve performance of :func:`utils.get` by around 4-6x depending on usage.
- Improve performance of event parsing lookup by around 2.5x.
- Keyword arguments in :meth:`Client.start` and :meth:`Client.run` are now validated (:issue-dpy:`953`, :issue-dpy:`2170`)
- The Discord error code is now shown in the exception message for :exc:`HTTPException`.
- Internal tasks launched by the library will now have their own custom ``__repr__``.
- All public facing types should now have a proper and more detailed ``__repr__``.
- |tasks| Errors are now logged via the standard :mod:`py:logging` module.

.. _vp1p1p1:

v1.1.1
--------

Bug Fixes
~~~~~~~~~~~~

- Webhooks do not overwrite data on retrying their HTTP requests (:issue-dpy:`2140`)

Miscellaneous
~~~~~~~~~~~~~~

- Add back signal handling to :meth:`Client.run` due to issues some users had with proper cleanup.

.. _vp1p1p0:

v1.1.0
---------

New Features
~~~~~~~~~~~~~~

- **There is a new extension dedicated to making background tasks easier.**
    - You can check the documentation here: :ref:`ext_tasks_api`.
- Add :attr:`Permissions.stream` permission. (:issue-dpy:`2077`)
- Add equality comparison and hash support to :class:`Asset`
- Add ``compute_prune_members`` parameter to :meth:`Guild.prune_members` (:issue-dpy:`2085`)
- Add :attr:`Client.cached_messages` attribute to fetch the message cache (:issue-dpy:`2086`)
- Add :meth:`abc.GuildChannel.clone` to clone a guild channel. (:issue-dpy:`2093`)
- Add ``delay`` keyword-only argument to :meth:`Message.delete` (:issue-dpy:`2094`)
- Add support for ``<:name:id>`` when adding reactions (:issue-dpy:`2095`)
- Add :meth:`Asset.read` to fetch the bytes content of an asset (:issue-dpy:`2107`)
- Add :meth:`Attachment.read` to fetch the bytes content of an attachment (:issue-dpy:`2118`)
- Add support for voice kicking by passing ``None`` to :meth:`Member.move_to`.

``disnake.ext.commands``
++++++++++++++++++++++++++

- Add new :func:`~.commands.dm_only` check.
- Support callable converters in :data:`~.commands.Greedy`
- Add new :class:`~.commands.MessageConverter`.
    - This allows you to use :class:`Message` as a type hint in functions.
- Allow passing ``cls`` in the :func:`~.commands.group` decorator (:issue-dpy:`2061`)
- Add :attr:`.Command.parents` to fetch the parents of a command (:issue-dpy:`2104`)


Bug Fixes
~~~~~~~~~~~~

- Fix :exc:`AttributeError` when using ``__repr__`` on :class:`Widget`.
- Fix issue with :attr:`abc.GuildChannel.overwrites` returning ``None`` for keys.
- Remove incorrect legacy NSFW checks in e.g. :meth:`TextChannel.is_nsfw`.
- Fix :exc:`UnboundLocalError` when :class:`RequestsWebhookAdapter` raises an error.
- Fix bug where updating your own user did not update your member instances.
- Tighten constraints of ``__eq__`` in :class:`Spotify` objects (:issue-dpy:`2113`, :issue-dpy:`2117`)

``disnake.ext.commands``
++++++++++++++++++++++++++

- Fix lambda converters in a non-module context (e.g. ``eval``).
- Use message creation time for reference time when computing cooldowns.
    - This prevents cooldowns from triggering during e.g. a RESUME session.
- Fix the default :func:`on_command_error` to work with new-style cogs (:issue-dpy:`2094`)
- DM channels are now recognised as NSFW in :func:`~.commands.is_nsfw` check.
- Fix race condition with help commands (:issue-dpy:`2123`)
- Fix cog descriptions not showing in :class:`~.commands.MinimalHelpCommand` (:issue-dpy:`2139`)

Miscellaneous
~~~~~~~~~~~~~~~

- Improve the performance of internal enum creation in the library by about 5x.
- Make the output of ``python -m disnake --version`` a bit more useful.
- The loop cleanup facility has been rewritten again.
- The signal handling in :meth:`Client.run` has been removed.

``disnake.ext.commands``
++++++++++++++++++++++++++

- Custom exception classes are now used for all default checks in the library (:issue-dpy:`2101`)


.. _vp1p0p1:

v1.0.1
--------

Bug Fixes
~~~~~~~~~~~

- Fix issue with speaking state being cast to ``int`` when it was invalid.
- Fix some issues with loop cleanup that some users experienced on Linux machines.
- Fix voice handshake race condition (:issue-dpy:`2056`, :issue-dpy:`2063`)

.. _vp1p0p0:

v1.0.0
--------

The changeset for this version are too big to be listed here, for more information please
see :ref:`the migrating page <migrating_1_0>`.


.. _vp0p16p6:

v0.16.6
--------

Bug Fixes
~~~~~~~~~~

- Fix issue with :meth:`Client.create_server` that made it stop working.
- Fix main thread being blocked upon calling ``StreamPlayer.stop``.
- Handle HEARTBEAT_ACK and resume gracefully when it occurs.
- Fix race condition when pre-emptively rate limiting that caused releasing an already released lock.
- Fix invalid state errors when immediately cancelling a coroutine.

.. _vp0p16p1:

v0.16.1
--------

This release is just a bug fix release with some better rate limit implementation.

Bug Fixes
~~~~~~~~~~~

- Servers are now properly chunked for user bots.
- The CDN URL is now used instead of the API URL for assets.
- Rate limit implementation now tries to use header information if possible.
- Event loop is now properly propagated (:issue-dpy:`420`)
- Allow falsey values in :meth:`Client.send_message` and :meth:`Client.send_file`.

.. _vp0p16p0:

v0.16.0
---------

New Features
~~~~~~~~~~~~~~

- Add :attr:`Channel.overwrites` to get all the permission overwrites of a channel.
- Add :attr:`Server.features` to get information about partnered servers.

Bug Fixes
~~~~~~~~~~

- Timeout when waiting for offline members while triggering :func:`on_ready`.

    - The fact that we did not timeout caused a gigantic memory leak in the library that caused
      thousands of duplicate :class:`Member` instances causing big memory spikes.

- Discard null sequences in the gateway.

    - The fact these were not discarded meant that :func:`on_ready` kept being called instead of
      :func:`on_resumed`. Since this has been corrected, in most cases :func:`on_ready` will be
      called once or twice with :func:`on_resumed` being called much more often.

.. _vp0p15p1:

v0.15.1
---------

- Fix crash on duplicate or out of order reactions.

.. _vp0p15p0:

v0.15.0
--------

New Features
~~~~~~~~~~~~~~

- Rich Embeds for messages are now supported.

    - To do so, create your own :class:`Embed` and pass the instance to the ``embed`` keyword argument to :meth:`Client.send_message` or :meth:`Client.edit_message`.
- Add :meth:`Client.clear_reactions` to remove all reactions from a message.
- Add support for MESSAGE_REACTION_REMOVE_ALL event, under :func:`on_reaction_clear`.
- Add :meth:`Permissions.update` and :meth:`PermissionOverwrite.update` for bulk permission updates.

    - This allows you to use e.g. ``p.update(read_messages=True, send_messages=False)`` in a single line.
- Add :meth:`PermissionOverwrite.is_empty` to check if the overwrite is empty (i.e. has no overwrites set explicitly as true or false).

For the command extension, the following changed:

- ``Context`` is no longer slotted to facilitate setting dynamic attributes.

.. _vp0p14p3:

v0.14.3
---------

Bug Fixes
~~~~~~~~~~~

- Fix crash when dealing with MESSAGE_REACTION_REMOVE
- Fix incorrect buckets for reactions.

.. _v0p14p2:

v0.14.2
---------

New Features
~~~~~~~~~~~~~~

- :meth:`Client.wait_for_reaction` now returns a namedtuple with ``reaction`` and ``user`` attributes.
    - This is for better support in the case that ``None`` is returned since tuple unpacking can lead to issues.

Bug Fixes
~~~~~~~~~~

- Fix bug that disallowed ``None`` to be passed for ``emoji`` parameter in :meth:`Client.wait_for_reaction`.

.. _v0p14p1:

v0.14.1
---------

Bug fixes
~~~~~~~~~~

- Fix bug with `Reaction` not being visible at import.
    - This was also breaking the documentation.

.. _v0p14p0:

v0.14.0
--------

This update adds new API features and a couple of bug fixes.

New Features
~~~~~~~~~~~~~

- Add support for Manage Webhooks permission under :attr:`Permissions.manage_webhooks`
- Add support for ``around`` argument in 3.5+ :meth:`Client.logs_from`.
- Add support for reactions.
    - :meth:`Client.add_reaction` to add a reactions
    - :meth:`Client.remove_reaction` to remove a reaction.
    - :meth:`Client.get_reaction_users` to get the users that reacted to a message.
    - :attr:`Permissions.add_reactions` permission bit support.
    - Two new events, :func:`on_reaction_add` and :func:`on_reaction_remove`.
    - :attr:`Message.reactions` to get reactions from a message.
    - :meth:`Client.wait_for_reaction` to wait for a reaction from a user.

Bug Fixes
~~~~~~~~~~

- Fix bug with Paginator still allowing lines that are too long.
- Fix the :attr:`Permissions.manage_emojis` bit being incorrect.

.. _v0p13p0:

v0.13.0
---------

This is a backwards compatible update with new features.

New Features
~~~~~~~~~~~~~

- Add the ability to manage emojis.

    - :meth:`Client.create_custom_emoji` to create new emoji.
    - :meth:`Client.edit_custom_emoji` to edit an old emoji.
    - :meth:`Client.delete_custom_emoji` to delete a custom emoji.
- Add new :attr:`Permissions.manage_emojis` toggle.

    - This applies for :class:`PermissionOverwrite` as well.
- Add new statuses for :class:`Status`.

    - :attr:`Status.dnd` (aliased with :attr:`Status.do_not_disturb`\) for Do Not Disturb.
    - :attr:`Status.invisible` for setting your status to invisible (please see the docs for a caveat).
- Deprecate :meth:`Client.change_status`

    - Use :meth:`Client.change_presence` instead for better more up to date functionality.
    - This method is subject for removal in a future API version.
- Add :meth:`Client.change_presence` for changing your status with the new Discord API change.

    - This is the only method that allows changing your status to invisible or do not disturb.

Bug Fixes
~~~~~~~~~~

- Paginator pages do not exceed their max_size anymore (:issue-dpy:`340`)
- Do Not Disturb users no longer show up offline due to the new :class:`Status` changes.

.. _v0p12p0:

v0.12.0
---------

This is a bug fix update that also comes with new features.

New Features
~~~~~~~~~~~~~

- Add custom emoji support.

    - Adds a new class to represent a custom Emoji named :class:`Emoji`
    - Adds a utility generator function, :meth:`Client.get_all_emojis`.
    - Adds a list of emojis on a server, :attr:`Server.emojis`.
    - Adds a new event, :func:`on_server_emojis_update`.
- Add new server regions to :class:`ServerRegion`

    - :attr:`ServerRegion.eu_central` and :attr:`ServerRegion.eu_west`.
- Add support for new pinned system message under :attr:`MessageType.pins_add`.
- Add order comparisons for :class:`Role` to allow it to be compared with regards to hierarchy.

    - This means that you can now do ``role_a > role_b`` etc to check if ``role_b`` is lower in the hierarchy.

- Add :attr:`Server.role_hierarchy` to get the server's role hierarchy.
- Add :attr:`Member.server_permissions` to get a member's server permissions without their channel specific overwrites.
- Add :meth:`Client.get_user_info` to retrieve a user's info from their ID.
- Add a new ``Player`` property, ``Player.error`` to fetch the error that stopped the player.

    - To help with this change, a player's ``after`` function can now take a single parameter denoting the current player.
- Add support for server verification levels.

    - Adds a new enum called :class:`VerificationLevel`.
    - This enum can be used in :meth:`Client.edit_server` under the ``verification_level`` keyword argument.
    - Adds a new attribute in the server, :attr:`Server.verification_level`.
- Add :attr:`Server.voice_client` shortcut property for :meth:`Client.voice_client_in`.

    - This is technically old (was added in v0.10.0) but was undocumented until v0.12.0.

For the command extension, the following are new:

- Add custom emoji converter.
- All default converters that can take IDs can now convert via ID.
- Add coroutine support for ``Bot.command_prefix``.
- Add a method to reset command cooldown.

Bug Fixes
~~~~~~~~~~

- Fix bug that caused the library to not work with the latest ``websockets`` library.
- Fix bug that leaked keep alive threads (:issue-dpy:`309`)
- Fix bug that disallowed :class:`ServerRegion` from being used in :meth:`Client.edit_server`.
- Fix bug in :meth:`Channel.permissions_for` that caused permission resolution to happen out of order.
- Fix bug in :attr:`Member.top_role` that did not account for same-position roles.

.. _v0p11p0:

v0.11.0
--------

This is a minor bug fix update that comes with a gateway update (v5 -> v6).

Breaking Changes
~~~~~~~~~~~~~~~~~

- ``Permissions.change_nicknames`` has been renamed to :attr:`Permissions.change_nickname` to match the UI.

New Features
~~~~~~~~~~~~~

- Add the ability to prune members via :meth:`Client.prune_members`.
- Switch the websocket gateway version to v6 from v5. This allows the library to work with group DMs and 1-on-1 calls.
- Add :attr:`AppInfo.owner` attribute.
- Add :class:`CallMessage` for group voice call messages.
- Add :class:`GroupCall` for group voice call information.
- Add :attr:`Message.system_content` to get the system message.
- Add the remaining VIP servers and the Brazil servers into :class:`ServerRegion` enum.
- Add ``stderr`` argument to :meth:`VoiceClient.create_ffmpeg_player` to redirect stderr.
- The library now handles implicit permission resolution in :meth:`Channel.permissions_for`.
- Add :attr:`Server.mfa_level` to query a server's 2FA requirement.
- Add :attr:`Permissions.external_emojis` permission.
- Add :attr:`Member.voice` attribute that refers to a :class:`VoiceState`.

    - For backwards compatibility, the member object will have properties mirroring the old behaviour.

For the command extension, the following are new:

- Command cooldown system with the ``cooldown`` decorator.
- ``UserInputError`` exception for the hierarchy for user input related errors.

Bug Fixes
~~~~~~~~~~

- :attr:`Client.email` is now saved when using a token for user accounts.
- Fix issue when removing roles out of order.
- Fix bug where discriminators would not update.
- Handle cases where ``HEARTBEAT`` opcode is received. This caused bots to disconnect seemingly randomly.

For the command extension, the following bug fixes apply:

- ``Bot.check`` decorator is actually a decorator not requiring parentheses.
- ``Bot.remove_command`` and ``Group.remove_command`` no longer throw if the command doesn't exist.
- Command names are no longer forced to be ``lower()``.
- Fix a bug where Member and User converters failed to work in private message contexts.
- ``HelpFormatter`` now ignores hidden commands when deciding the maximum width.

.. _v0p10p0:

v0.10.0
-------

For breaking changes, see :ref:`migrating-to-async`. The breaking changes listed there will not be enumerated below. Since this version is rather a big departure from v0.9.2, this change log will be non-exhaustive.

New Features
~~~~~~~~~~~~~

- The library is now fully ``asyncio`` compatible, allowing you to write non-blocking code a lot more easily.
- The library now fully handles 429s and unconditionally retries on 502s.
- A new command extension module was added but is currently undocumented. Figuring it out is left as an exercise to the reader.
- Two new exception types, :exc:`Forbidden` and :exc:`NotFound` to denote permission errors or 404 errors.
- Added :meth:`Client.delete_invite` to revoke invites.
- Added support for sending voice. Check :class:`VoiceClient` for more details.
- Added :meth:`Client.wait_for_message` coroutine to aid with follow up commands.
- Added :data:`version_info` named tuple to check version info of the library.
- Login credentials are now cached to have a faster login experience. You can disable this by passing in ``cache_auth=False``
  when constructing a :class:`Client`.
- New utility function, :func:`disnake.utils.get` to simplify retrieval of items based on attributes.
- All data classes now support ``!=``, ``==``, ``hash(obj)`` and ``str(obj)``.
- Added :meth:`Client.get_bans` to get banned members from a server.
- Added :meth:`Client.invites_from` to get currently active invites in a server.
- Added :attr:`Server.me` attribute to get the :class:`Member` version of :attr:`Client.user`.
- Most data classes now support a ``hash(obj)`` function to allow you to use them in ``set`` or ``dict`` classes or subclasses.
- Add :meth:`Message.clean_content` to get a text version of the content with the user and channel mentioned changed into their names.
- Added a way to remove the messages of the user that just got banned in :meth:`Client.ban`.
- Added :meth:`Client.wait_until_ready` to facilitate easy creation of tasks that require the client cache to be ready.
- Added :meth:`Client.wait_until_login` to facilitate easy creation of tasks that require the client to be logged in.
- Add :class:`disnake.Game` to represent any game with custom text to send to :meth:`Client.change_status`.
- Add :attr:`Message.nonce` attribute.
- Add :meth:`Member.permissions_in` as another way of doing :meth:`Channel.permissions_for`.
- Add :meth:`Client.move_member` to move a member to another voice channel.
- You can now create a server via :meth:`Client.create_server`.
- Added :meth:`Client.edit_server` to edit existing servers.
- Added :meth:`Client.server_voice_state` to server mute or server deafen a member.
- If you are being rate limited, the library will now handle it for you.
- Add :func:`on_member_ban` and :func:`on_member_unban` events that trigger when a member is banned/unbanned.

Performance Improvements
~~~~~~~~~~~~~~~~~~~~~~~~~

- All data classes now use ``__slots__`` which greatly reduce the memory usage of things kept in cache.
- Due to the usage of ``asyncio``, the CPU usage of the library has gone down significantly.
- A lot of the internal cache lists were changed into dictionaries to change the ``O(n)`` lookup into ``O(1)``.
- Compressed READY is now on by default. This means if you're on a lot of servers (or maybe even a few) you would
  receive performance improvements by having to download and process less data.
- While minor, change regex from ``\d+`` to ``[0-9]+`` to avoid unnecessary unicode character lookups.

Bug Fixes
~~~~~~~~~~

- Fix bug where guilds being updated did not edit the items in cache.
- Fix bug where ``member.roles`` were empty upon joining instead of having the ``@everyone`` role.
- Fix bug where :meth:`Role.is_everyone` was not being set properly when the role was being edited.
- :meth:`Client.logs_from` now handles cases where limit > 100 to sidestep the disnake API limitation.
- Fix bug where a role being deleted would trigger a ``ValueError``.
- Fix bug where :meth:`Permissions.kick_members` and :meth:`Permissions.ban_members` were flipped.
- Mentions are now triggered normally. This was changed due to the way disnake handles it internally.
- Fix issue when a :class:`Message` would attempt to upgrade a :attr:`Message.server` when the channel is
  a :class:`Object`.
- Unavailable servers were not being added into cache, this has been corrected.
