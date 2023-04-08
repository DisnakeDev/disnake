.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

.. |commands| replace:: [:ref:`ext.commands <disnake_ext_commands>`]
.. |tasks| replace:: [:ref:`ext.tasks <disnake_ext_tasks>`]

.. _whats_new:

Changelog
=========

This page keeps a detailed human friendly rendering of what's new and changed
in specific versions.

.. towncrier-draft-entries:: |release| [UNRELEASED]

.. towncrier release notes start

.. _vp2p8p1:

v2.8.1
------

Bug Fixes
~~~~~~~~~
- Fix :class:`VoiceClient` not continuing to play audio when moving between channels. (:issue:`845`)
- Fix KeepAlive logging un-intentionally attempting to interpolate stack trace logger calls (:issue:`940`)
- Fix attribute error when attempting to access :class:`DMChannel.flags` under certain circumstances. (:issue:`960`)
- Fix voice connection discovery using incorrect packet sizes. (:issue:`967`)

Documentation
~~~~~~~~~~~~~
- Update automod rule limits. (:issue:`931`)

.. _vp2p8p0:

v2.8.0
------

This release comes with support for NSFW application commands,
the :func:`on_audit_log_entry_create` event,
and a new :class:`Event` enum for use with methods like :func:`Client.wait_for`.

Breaking Changes
~~~~~~~~~~~~~~~~
- :attr:`StickerPack.cover_sticker_id`, :attr:`.cover_sticker <StickerPack.cover_sticker>` and :attr:`.banner <StickerPack.banner>` are now optional and may return ``None``. (:issue:`912`)
- :attr:`AuditLogEntry.user` may now be an :class:`Object` if the user cannot be found, particularly in entries from the :func:`on_audit_log_entry_create` event. (:issue:`920`)

New Features
~~~~~~~~~~~~
- Add :class:`GuildBuilder` and :func:`Client.guild_builder` for full coverage of the guild creation endpoint. (:issue:`578`)
- Support regex within automod using :attr:`AutoModTriggerMetadata.regex_patterns`. (:issue:`794`)
- Add :attr:`File.closed` and :attr:`File.bytes_length` properties. (:issue:`839`)
- Add :attr:`TextChannel.default_thread_slowmode_delay`. (:issue:`854`)
- Add support for NSFW application commands. (:issue:`865`)
    - Add :attr:`ApplicationCommand.nsfw`.
    - Add ``nsfw`` parameter to command constructors and decorators.
- Add :attr:`.UserFlags.active_developer` and :attr:`PublicUserFlags.active_developer`. (:issue:`866`)
- Adds reasons/descriptions to :exc:`ConnectionClosed` errors. (:issue:`873`)
- Update :class:`AutoModTriggerMetadata` overloads to allow passing ``allow_list`` to keyword-based rules. (:issue:`877`)
- The :attr:`PublicUserFlags.discord_certified_moderator` is now an alias of :attr:`PublicUserFlags.moderator_programs_alumni`. (:issue:`883`)
- Add :attr:`ForumChannel.default_layout`, and ``default_layout`` parameter to channel edit methods. (:issue:`885`, :issue:`903`)
- Add :attr:`Locale.id` (Indonesian) locale. (:issue:`890`)
- Adds :class:`Event` enumeration to use in :meth:`Client.wait_for`, :meth:`disnake.ext.commands.Bot.wait_for` and in :func:`disnake.ext.commands.Bot.listen` decorator. (:issue:`895`)
- Add new :attr:`MessageType.interaction_premium_upsell` and :attr:`MessageType.guild_application_premium_subscription` message types. (:issue:`905`)
- Add application role connection features. (:issue:`906`)
    - Add :class:`ApplicationRoleConnectionMetadata` and :class:`ApplicationRoleConnectionMetadataType` types.
    - Add :class:`Client.fetch_role_connection_metadata` and :class:`Client.edit_role_connection_metadata` methods.
    - Add :attr:`RoleTags.is_linked_role` and :attr:`AppInfo.role_connections_verification_url` attributes.
- Add :attr:`StickerFormatType.gif`. (:issue:`910`)
- Add support for the :func:`on_audit_log_entry_create` gateway event, and add :attr:`Intents.moderation` intent. :attr:`Intents.bans` is now an alias of :attr:`Intents.moderation`. (:issue:`915`)
- Add :attr:`~Member.flags` property to :class:`Member`. (:issue:`918`)
- Add fallback to :class:`Object` for :attr:`AuditLogEntry.user` (:issue:`920`)

Bug Fixes
~~~~~~~~~
- |commands| Fix ``help_command`` parameter annotations to allow ``None`` value. (:issue:`849`)
- Fix user cache memory leak where unused objects weren't being evicted (provided that :attr:`Intents.members` is enabled). (:issue:`858`)
- Fix :attr:`Message.author.public_flags <Member.public_flags>` always being ``0`` when the member cache is disabled. (:issue:`870`)
- Export missing ``ThreadWithMessage`` class. (:issue:`879`)
- Add previously missing ``applied_tags`` parameter to all :meth:`ForumChannel.create_thread` overloads. (:issue:`880`)
- Fix conversion of custom emoji strings (e.g. ``<:this:934852112221872198>``) in :meth:`Message.add_reaction` and similar methods to more strictly adhere to the API documentation. (:issue:`887`)
- Fix :meth:`Client.delete_guild_command` not updating the local command cache. (:issue:`907`)
- Fix errors when trying to deserialize stickers with unknown formats. (:issue:`911`)
- Make :attr:`StickerPack.cover_sticker_id`, :attr:`.cover_sticker <StickerPack.cover_sticker>` and :attr:`.banner <StickerPack.banner>` optional. (:issue:`912`)
- Fix handling of ``ECONNRESET`` errors on Linux. (:issue:`921`)

Documentation
~~~~~~~~~~~~~
- Enable `OpenSearch <https://developer.mozilla.org/en-US/docs/Web/OpenSearch>`_, allowing easy integration of the search functionality into browsers. (:issue:`859`)
- Clarify types of optional :class:`Invite` attributes. (:issue:`864`)
- Remove documentation regarding private threads requiring boosts. (:issue:`872`)
- Update :class:`AutoModTriggerMetadata` field limits. (:issue:`877`)

Miscellaneous
~~~~~~~~~~~~~
- Declare a :pep:`517` build backend in pyproject.toml, and use :pep:`621` to define most package metadata. (:issue:`830`)

.. _vp2p7p2:

v2.7.2
------

Bug Fixes
~~~~~~~~~
- Fix :class:`VoiceClient` not continuing to play audio when moving between channels. (:issue:`845`)
- Fix KeepAlive logging un-intentionally attempting to interpolate stack trace logger calls (:issue:`940`)
- Fix attribute error when attempting to access :class:`DMChannel.flags` under certain circumstances. (:issue:`960`)
- Fix voice connection discovery using incorrect packet sizes. (:issue:`967`)

.. _vp2p7p1:

v2.7.1
------

Bug Fixes
~~~~~~~~~
- Fix :attr:`Message.author.public_flags <Member.public_flags>` always being ``0`` when the member cache is disabled. (:issue:`870`)
- Export missing ``ThreadWithMessage`` class. (:issue:`879`)
- Fix :meth:`Client.delete_guild_command` not updating the local command cache. (:issue:`907`)
- Fix errors when trying to deserialize stickers with unknown formats. (:issue:`911`)

.. _vp2p7p0:

v2.7.0
------

This release comes with support for python 3.11 and new selects.

Breaking Changes
~~~~~~~~~~~~~~~~
- Properly document that :attr:`Message.system_content` may return ``None``. While this is documented as a breaking change, this function always could return ``None`` if the message type was not recognised. (:issue:`766`)
- Rename :meth:`InteractionDataResolved.get` to :meth:`~InteractionDataResolved.get_by_id`. (:issue:`814`)

Deprecations
~~~~~~~~~~~~
- Rename :class:`ApplicationCommandInteractionDataResolved` to :class:`InteractionDataResolved`. (:issue:`814`)
- |commands| Deprecate the ``sync_commands``, ``sync_commands_debug``, and  ``sync_commands_on_cog_unload`` parameters of :class:`~disnake.ext.commands.Bot` and :class:`~disnake.ext.commands.InteractionBot`. These have been replaced with the ``command_sync_flags`` parameter which takes a :class:`~disnake.ext.commands.CommandSyncFlags` instance. (:issue:`806`)

New Features
~~~~~~~~~~~~
- Update :attr:`Message.system_content` to be accurate to the client as of October 2022. (:issue:`766`)
    - This also properly documents that it is possible to return ``None``.
- Add type hints to all flag constructors, now supporting type-checking for creating flag classes (e.g. ``Intents(members=True)``) which used to be untyped. (:issue:`778`)
- Add :func:`GuildScheduledEvent.start`, :func:`.end <GuildScheduledEvent.end>` and :func:`.cancel <GuildScheduledEvent.cancel>` shortcuts. (:issue:`781`)
- Support Python 3.11. (:issue:`785`, :issue:`827`, :issue:`829`, :issue:`833`)
- Improve the cli, allowing the usage of :class:`.ext.commands.InteractionBot`, :class:`.ext.commands.AutoShardedInteractionBot`. (:issue:`791`)
- Add new select menu components. (:issue:`800`, :issue:`803`)
    - Add new :class:`ComponentType` values.
    - Add :class:`UserSelectMenu`, :class:`RoleSelectMenu`, :class:`MentionableSelectMenu`, :class:`ChannelSelectMenu` components.
    - Add :class:`ui.UserSelect`, :class:`ui.RoleSelect`, :class:`ui.MentionableSelect`, :class:`ui.ChannelSelect` UI types.
    - Add :func:`ui.user_select`, :func:`ui.role_select`, :func:`ui.mentionable_select`, :func:`ui.channel_select` decorators.
    - Add :func:`ui.ActionRow.add_user_select`, :func:`add_role_select() <ui.ActionRow.add_role_select>`, :func:`add_mentionable_select() <ui.ActionRow.add_mentionable_select>`, :func:`add_channel_select() <ui.ActionRow.add_channel_select>`
    - Renamed string select types for clarity (previous names will continue to work):
        - :class:`SelectMenu` -> :class:`StringSelectMenu`
        - :class:`ui.Select` -> :class:`ui.StringSelect`
        - :func:`ui.select` -> :func:`ui.string_select`
        - :func:`ui.ActionRow.add_select` -> :func:`ui.ActionRow.add_string_select`
    - Add :attr:`MessageInteraction.resolved_values` and :attr:`MessageInteractionData.resolved`.
- Support ``delete_after`` parameter when sending ephemeral interaction responses. (:issue:`816`)
- Allow ``slowmode_delay`` parameter of :meth:`ForumChannel.create_thread` to be optional. (:issue:`822`)
- Add ``suppress_embeds`` parameter to :meth:`Interaction.edit_original_response` and :meth:`InteractionMessage.edit`. (:issue:`832`)
- |commands| Add :class:`~disnake.ext.commands.CommandSyncFlags` to provide sync configuration to :class:`~disnake.ext.commands.Bot` and :class:`~disnake.ext.commands.InteractionBot` (and their autosharded variants) as ``command_sync_flags``. (:issue:`265`, :issue:`433`, :issue:`468`, :issue:`806`)

Bug Fixes
~~~~~~~~~
- Add the missing attributes for :class:`PermissionOverwrite`: ``use_application_commands`` and ``use_embedded_activities``. (:issue:`777`)
- Ensure that embed fields are copied properly by :func:`Embed.copy` and that the copied embed is completely separate from the original one. (:issue:`792`)
- Fix an issue with :meth:`Member.ban` erroring when the ``delete_message_days`` parameter was provided. (:issue:`810`)
- Try to get threads used in interactions (like threads in command arguments) from the cache first, before creating a new instance. (:issue:`814`)
- Fix creation of threads in text channels without :attr:`Permissions.manage_threads`. (:issue:`818`)
- Fix off-by-one error in :class:`AutoModKeywordPresets` values. (:issue:`820`)
- Update event loop handling to avoid warnings when running on Python 3.11. (:issue:`827`)
- |commands| Fix a case where optional variadic arguments could have infinite loops in parsing depending on the user input. (:issue:`825`)

Documentation
~~~~~~~~~~~~~
- Speed up page load by changing hoverxref tooltips to be lazily loaded. (:issue:`393`)
- Remove reference to the v1.0 migration guide from the main index page, and move legacy changelogs to a separate page. (:issue:`697`)
- Update sphinx from version 5.1 to 5.3. (:issue:`764`, :issue:`821`)
- Add a note warning mentioning that using a :class:`disnake.File` object as file kwarg makes a :class:`disnake.Embed` not reusable. (:issue:`786`)
- Update broken Discord API Docs links, add ``:ddocs:`` role for easily creating links to the API documentation. (:issue:`793`)
- Add a custom 404 page for when the navigated page does not exist. (:issue:`797`)

Miscellaneous
~~~~~~~~~~~~~
- Increase the upper bound for the ``aiohttp`` dependency from ``<3.9`` to ``<4``. (:issue:`789`)
- Use ``importlib.metadata`` instead of the deprecated ``pkg_resources`` in the cli for displaying the version. (:issue:`791`)
- |commands| Add missing ``py.typed`` marker. (:issue:`784`)
- |tasks| Add missing ``py.typed`` marker. (:issue:`784`)

.. _vp2p6p3:

v2.6.3
------

This maintainence release contains backports from v2.8.0.

Bug Fixes
~~~~~~~~~
- Fix :attr:`Message.author.public_flags <Member.public_flags>` always being ``0`` when the member cache is disabled. (:issue:`870`)
- Export missing ``ThreadWithMessage`` class. (:issue:`879`)
- Fix :meth:`Client.delete_guild_command` not updating the local command cache. (:issue:`907`)
- Fix errors when trying to deserialize stickers with unknown formats. (:issue:`911`)

.. _vp2p6p2:

v2.6.2
------

This maintainence release contains backports from v2.7.0.

Bug Fixes
~~~~~~~~~
- Fix creation of threads in text channels without :attr:`Permissions.manage_threads`. (:issue:`818`)
- Fix off-by-one error in :class:`AutoModKeywordPresets` values. (:issue:`820`)
- |commands| Fix a case where optional variadic arguments could have infinite loops in parsing depending on the user input. (:issue:`825`)

.. _vp2p6p1:

v2.6.1
------

This maintainence release contains backports from v2.7.0.

Bug Fixes
~~~~~~~~~
- Ensure that embed fields are copied properly by :func:`Embed.copy` and that the copied embed is completely separate from the original one. (:issue:`792`)
- Fix an issue with :meth:`Member.ban` erroring when the ``delete_message_days`` parameter was provided. (:issue:`810`)

.. _vp2p6p0:

v2.6.0
------

This release adds support for new forum channel features (like tags) as well as auto moderation, among other things. See below for more.

Also note the breaking changes listed below, which may require additional code changes.

Breaking Changes
~~~~~~~~~~~~~~~~

- Update :class:`Client` classes such that their initialization kwargs are explicitly stated and typehinted. (:issue:`371`)
    - Replaced ``**kwargs`` / ``**options`` with explicit keyword arguments for the ``__init__`` methods of :class:`Client`, :class:`ext.commands.Bot`, :class:`ext.commands.InteractionBot`, all ``AutoSharded*`` variants, and all relevant parent classes.
- Call new :func:`disnake.on_gateway_error` instead of letting exceptions propagate that occurred while deserializing a received gateway event. (:issue:`401`)
- Rework :class:`.Embed` internals. (:issue:`435`)
    - :meth:`Embed.set_footer` now requires the ``text`` parameter.
    - :attr:`Embed.type` is now optional, although this could previously be ``Embed.Empty``.
    - ``EmptyEmbed`` and ``Embed.Empty`` are deprecated in favor of ``None``, have been removed from the documentation, and will result in type-checking errors.
- Refactor :class:`.ui.ActionRow` with complete typings. (:issue:`462`)
    - :attr:`.ui.ActionRow.children` now returns an immutable :class:`Sequence` instead of a :class:`list`.
- Remove ``InvalidArgument`` and replace it with :exc:`TypeError` and :exc:`ValueError`. (:issue:`471`)
- Rename ``channel_id`` parameter to ``channel`` on :attr:`Guild.create_scheduled_event` and :meth:`GuildScheduledEvent.edit`. (:issue:`548`, :issue:`590`)
- Raise :exc:`TypeError` instead of :exc:`ValueError` in :class:`GuildScheduledEvent` validation. (:issue:`560`)
- Assume the local timezone instead of UTC when providing naive datetimes to scheduled event related methods. (:issue:`579`)
- Update :class:`ModalInteraction` typings. (:issue:`583`)
    - ``ModalInteraction.walk_components`` is replaced by :meth:`ModalInteraction.walk_raw_components`.
- Change the default of the ``ignore_timeout`` parameter for all ``permissions_for`` methods to ``False``. (:issue:`672`)
- Update activity attributes to match API types. (:issue:`685`)
    - Make :attr:`Spotify.start`, :attr:`Spotify.end`, :attr:`Spotify.duration` optional.
    - Remove :attr:`Activity.timestamps`, values are accessible through :attr:`Activity.start`, :attr:`Activity.end`.
    - Change type of :attr:`Activity.buttons` to List[:class:`str`].
- Remove :attr:`WidgetMember.nick`; :attr:`WidgetMember.name` contains the member's nickname, if set. (:issue:`736`)
- |commands| Change :func:`has_permissions <ext.commands.has_permissions>` and :func:`bot_has_permissions <ext.commands.bot_has_permissions>` checks to take timeouts into consideration. (:issue:`318`, :issue:`672`)
- |commands| Change :func:`commands.register_injection <ext.commands.register_injection>` to now return an instance of :class:`Injection <ext.commands.Injection>`. (:issue:`669`)
- |commands| Changed parameters of :attr:`SubCommand <ext.commands.SubCommand>` and  :attr:`SubCommandGroup <ext.commands.SubCommandGroup>` to now require their parent command. (:issue:`759`)
    - This only affects code that creates an instance of SubCommand or SubCommandGroup manually by calling their constructors.
- |tasks| Change :class:`.ext.tasks.Loop` to use keyword-only parameters. (:issue:`655`)

Deprecations
~~~~~~~~~~~~

- ``EmptyEmbed`` and ``Embed.Empty`` are deprecated in favor of ``None``, have been removed from the documentation, and will result in type-checking errors. (:issue:`435`, :issue:`768`)
- The ``delete_message_days`` parameter of :func:`Guild.ban` and :func:`Member.ban` is deprecated in favour of ``clean_history_duration``. (:issue:`659`)
- |commands| Using ``command_prefix=None`` with :class:`~disnake.ext.commands.Bot` is now deprecated in favour of :class:`~disnake.ext.commands.InteractionBot`. (:issue:`689`)

New Features
~~~~~~~~~~~~

- Add custom type support for :func:`disnake.ui.button` and :func:`disnake.ui.select` decorators using ``cls`` parameter. (:issue:`281`)
- Add :func:`disnake.on_gateway_error`, :func:`Client.on_gateway_error` and ``enable_gateway_error_handler`` client parameter. (:issue:`401`)
- Update channel edit method annotations. (:issue:`418`)
    - ``slowmode_delay`` and ``default_auto_archive_duration`` are now optional.
    - ``category`` may now be any :class:`abc.Snowflake`, not necessarily a :class:`CategoryChannel`.
- Add new :class:`.ui.ActionRow` methods: :meth:`~.ui.ActionRow.insert_item`, :meth:`~.ui.ActionRow.clear_items`, :meth:`~.ui.ActionRow.remove_item`, :meth:`~.ui.ActionRow.pop`, as well as an ``index`` parameter for :meth:`~.ui.ActionRow.add_button`. (:issue:`462`)
    - Also support item access/deletion through ``row[i]``.
- Expose the icon and recipient data for :class:`Invite`\s whose target is a channel of type :attr:`ChannelType.group`. (:issue:`498`)
- Implement auto moderation. (:issue:`530`, :issue:`698`, :issue:`757`)
    - New types: :class:`AutoModAction`, :class:`AutoModTriggerMetadata`, :class:`AutoModRule`, :class:`AutoModActionExecution`
    - New enums: :class:`AutoModTriggerType`, :class:`AutoModEventType`, :class:`AutoModActionType`
    - New flags: :class:`AutoModKeywordPresets`
    - New methods: :func:`Guild.create_automod_rule`, :func:`Guild.fetch_automod_rule`, :func:`Guild.fetch_automod_rules`
    - New intents: :attr:`Intents.automod_configuration`, :attr:`Intents.automod_execution` (+ :attr:`Intents.automod` shortcut for both)
    - New events: :func:`on_automod_rule_create`, :func:`on_automod_rule_update`, :func:`on_automod_rule_delete`, :func:`on_automod_action_execution`
    - \+ all the relevant :class:`AuditLogEntry` and :class:`AuditLogChanges` fields.
- Expose additional provided objects by Discord in audit log handling. (:issue:`532`)
    - Also adds :class:`PartialIntegration`, and an ``integration`` attribute on :attr:`AuditLogEntry.extra` when the type is :attr:`AuditLogAction.application_command_permission_update`.
- Add :attr:`.Webhook.application_id` for accessing the ID of the app that created the webhook, if any. (:issue:`534`)
- Use :attr:`SessionStartLimit.remaining` when attempting to connect to Discord. (:issue:`537`)
    - Now raises :exc:`SessionStartLimitReached` if there are not enough remaining starts to start the client.
- Add multiple converters for previously undocumented fields for audit logs. (:issue:`546`)

    :class:`AuditLogDiff` can now have the following attributes with the specified types:

    - :attr:`~AuditLogDiff.flags` --- :class:`ChannelFlags`
    - :attr:`~AuditLogDiff.system_channel_flags` --- :class:`SystemChannelFlags`

    ``AuditLogDiff.unicode_emoji``, used for role icons, was renamed to :attr:`AuditLogDiff.emoji`.
- Implement :class:`ChannelFlags` on all channel types. (:issue:`547`)
- Make all \*InteractionData dataclasses dicts (:class:`MessageInteractionData`, :class:`ApplicationCommandInteractionData`, and so on). (:issue:`549`)
- Add support for :class:`.Webhook` in :class:`ForumChannel` instances. (:issue:`550`)
- Add :attr:`GuildScheduledEvent.created_at` and :attr:`GuildScheduledEvent.url` properties. (:issue:`561`)
- Add the :func:`Embed.check_limits` method to check if an Embed would be rejected from Discord. (:issue:`567`)
- Add ``bitrate`` parameter to :meth:`Guild.create_stage_channel`. (:issue:`571`)
- Add :meth:`Guild.edit_mfa_level` for modifying the guild's MFA level. (:issue:`574`)
- Add the ``slowmode_delay`` parameter to :meth:`Guild.create_voice_channel`. (:issue:`582`)
- Add :attr:`ModalInteractionData.components`. (:issue:`583`)
- Add the :attr:`Interaction.app_permissions` property, which shows the app permissions in the channel. (:issue:`586`)
- Allow ``entity_type`` parameter :attr:`Guild.create_scheduled_event` to be missing. (:issue:`590`)
- Add ``min_length`` and ``max_length`` support to :class:`.Option` and :class:`.ext.commands.Param`. (:issue:`593`)
- Add :attr:`.AllowedMentions.from_message` for constructing an allowed mentions object from a :class:`Message`. (:issue:`603`)
- Add support of more operators to all ``Flag`` classes. This list includes :class:`Intents` and :class:`Permissions`. (:issue:`605`, :issue:`615`, :issue:`616`)
    - ``&``, ``|``, ``^``, and ``~`` bitwise operator support.
    - ``<``, ``<=``, ``>``, and ``>=`` comparsion operator support.
    - Support ``|`` operators between flag instances and flag values.
    - Support ``~`` operator on flag values, which create a flag instance with all except this specific flag enabled.
    - Support ``|`` operators between flag values which create a flag instance with both flag values enabled.
- Support passing raw integer value to :class:`Intents` constructor. (:issue:`613`)
- Add :attr:`GuildScheduledEventStatus.cancelled` as an alias for :attr:`~GuildScheduledEventStatus.canceled`. (:issue:`630`)
- Add :func:`on_raw_member_remove` and :func:`on_raw_member_update` events, with the :class:`RawGuildMemberRemoveEvent` model. (:issue:`638`)
- Add :attr:`Thread.message_count`, :attr:`Thread.total_message_sent` and :attr:`Message.position` attributes. (:issue:`640`)
- Add support for setting :class:`ChannelFlags` directly when editing a channel or thread. (:issue:`642`)
- Add :attr:`ApplicationFlags.application_command_badge` flag which shows whether an application has at least one globally registered application command. (:issue:`649`)
- Add support for :attr:`Interaction.data` which guarantees that every subclass of ``Interaction`` has the ``data`` attribute. (:issue:`654`)
- Add ``clean_history_duration`` parameter to :func:`Guild.ban` and :func:`Member.ban`. (:issue:`659`)
- Add :attr:`Game.assets`. (:issue:`685`)
- Add permission typings to all methods that take permissions directly, for example :func:`disnake.abc.GuildChannel.set_permissions` and :func:`disnake.ext.commands.bot_has_permissions` to name a few. (:issue:`708`)
- Add :class:`GatewayParams` for configuring gateway connection parameters (e.g. disabling compression). (:issue:`709`)
- Add ``resume_gateway_url`` handling to gateway/websocket resume flow. (:issue:`709`, :issue:`769`)
- Add support for modifying the ``INVITES_DISABLED`` guild feature using :func:`Guild.edit`. (:issue:`718`)
- Implement remaining forum channel features. (:issue:`724`)
    - Add :class:`ForumTag` dataclass.
    - Add :attr:`ForumChannel.available_tags` and :attr:`Thread.applied_tags`.
    - Add :func:`ForumChannel.get_tag`, :func:`ForumChannel.get_tag_by_name`, :func:`Thread.add_tags` and :func:`Thread.remove_tags`.
    - Add :attr:`ForumChannel.default_thread_slowmode_delay`, :attr:`ForumChannel.default_reaction`, and :attr:`ForumChannel.default_sort_order`.
    - Add :attr:`ChannelFlags.require_tag` and :attr:`ForumChannel.requires_tag`.
    - New audit log fields for the above features.
- Add :attr:`BotIntegration.scopes`. (:issue:`729`)
- Return the :class:`disnake.ui.View` instance from :func:`View.add_item <disnake.ui.View.add_item>`, :func:`View.remove_item <disnake.ui.View.remove_item>` and :func:`View.clear_items <disnake.ui.View.clear_items>` to allow for fluent-style chaining. (:issue:`733`)
- Add :attr:`Widget.presence_count`. (:issue:`736`)
- Add :class:`InteractionResponse.type`, which contains the type of the response made, if any. (:issue:`737`)
- Add aliases to the ``original_message`` methods. (:issue:`738`)
    - :func:`Interaction.original_response` is aliased to :func:`Interaction.original_message`
    - :func:`Interaction.edit_original_response` is aliased to :func:`Interaction.edit_original_message`
    - :func:`Interaction.delete_original_response` is aliased to :func:`Interaction.delete_original_message`
- Change :func:`ForumChannel.create_thread` to not require the ``content`` parameter to be provided. (:issue:`739`)
    - Like :func:`TextChannel.send`, at least one of ``content``, ``embed``/``embeds``, ``file``/``files``, ``stickers``, ``components``, or ``view`` must be provided.
- Return the :class:`disnake.ui.ActionRow` instance on multiple methods to allow for fluent-style chaining. (:issue:`740`)
    - This applies to :func:`ActionRow.append_item <disnake.ui.ActionRow.append_item>`, :func:`ActionRow.insert_item <disnake.ui.ActionRow.insert_item>`, :func:`ActionRow.add_button <disnake.ui.ActionRow.add_button>`, :func:`ActionRow.add_select <disnake.ui.ActionRow.add_select>`, :func:`ActionRow.add_text_input <disnake.ui.ActionRow.add_text_input>`, :func:`ActionRow.clear_items <disnake.ui.ActionRow.clear_items>`, and :func:`ActionRow.remove_item <disnake.ui.ActionRow.remove_item>`.
- Add support for equality checks between two :class:`disnake.Embed`\s. (:issue:`742`)
- Add :attr:`Permissions.use_embedded_activities` as an alias for :attr:`Permissions.start_embedded_activities`. (:issue:`754`)
- Add :attr:`Permissions.use_application_commands` as an alias for :attr:`Permissions.use_slash_commands`. (:issue:`755`)
- Support setting ``with_message`` parameter of :class:`InteractionResponse.defer` for modal interactions to ``False``. (:issue:`758`)
- |commands| Add a way to get the parent or root commands of slash commands. (:issue:`277`)
    - Add :attr:`InvokableSlashCommand.parent <ext.commands.InvokableSlashCommand.parent>`, :attr:`SubCommandGroup.parent <ext.commands.SubCommandGroup.parent>`, and :attr:`SubCommand.parent <ext.commands.SubCommand.parent>`.
    - Add :attr:`InvokableSlashCommand.parents <ext.commands.InvokableSlashCommand.parents>`, :attr:`SubCommandGroup.parents <ext.commands.SubCommandGroup.parents>`, and :attr:`SubCommand.parents <ext.commands.SubCommand.parents>`.
    - Add :attr:`InvokableSlashCommand.root_parent <ext.commands.InvokableSlashCommand.root_parent>`, :attr:`SubCommandGroup.root_parent <ext.commands.SubCommandGroup.root_parent>`, and :attr:`SubCommand.root_parent <ext.commands.SubCommand.root_parent>`.
- |commands| Introduce :class:`commands.String <disnake.ext.commands.String>` for defining string option length limitations. (:issue:`593`)
- |commands| Add support for Union[:class:`User`, :class:`Role`] and Union[:class:`User`, :class:`Member`, :class:`Role`] annotations in slash commands. (:issue:`595`)
- |commands| Add support for injected parameters autocompletion (:issue:`670`)
    - Add :meth:`Injection.autocomplete <ext.commands.Injection.autocomplete>` decorator
    - Add :func:`injection <ext.commands.injection>` as a decorator interface for :func:`inject <ext.commands.inject>`
    - Add ``autocompleters`` keyword-only argument to :class:`Injection <ext.commands.Injection>`, :func:`inject <ext.commands.inject>`, and :func:`register_injection <ext.commands.register_injection>`
- |tasks| Add support for subclassing :class:`.ext.tasks.Loop` and using subclasses in :func:`.ext.tasks.loop` decorator. (:issue:`655`)

Bug Fixes
~~~~~~~~~

- Update incorrect channel edit method annotations. (:issue:`418`)
    - Fix ``sync_permissions`` parameter type.
    - Remove ``topic`` parameter from :func:`StageChannel.edit`, add ``bitrate``.
- Properly close sockets when receiving a voice server update event. (:issue:`488`)
- Warn the user that bools are not supported for ``default_member_permissions``. (:issue:`520`)
- Update the Guild Iterator to not get stuck in an infinite loop. (:issue:`526`)
    - Add a missing import for the scheduled event user iterator.
- Change the default guild :class:`.GuildSticker` limit to 5. (:issue:`531`)
- Handle optional :class:`Locale` instances (no longer create an enum value). (:issue:`533`)
- Update the type field handling for audit logs. (:issue:`535`)
    - :attr:`AuditLogDiff.type` objects are no longer always :class:`ChannelType` instances.
- Dispatch :func:`disnake.on_reaction_remove` for :class:`.Thread` instances. (:issue:`536`)
- Update :attr:`Guild.bitrate_limit` to use the correct value for the ``VIP_REGIONS`` feature flag. (:issue:`538`)
- Handle :class:`ThreadAutoArchiveDuration` instances for ``default_auto_archive_duration`` when editing channels. (:issue:`568`)
- Assume that ``None`` is an empty channel name and keep ``channel.name`` a string. (:issue:`569`)
- Remove the ``$`` prefix from ``IDENTIFY`` payload properties. (:issue:`572`)
- Replace old application command objects in cogs with the new/copied objects. (:issue:`575`)
- Fix opus function calls on arm64 macOS. (:issue:`620`)
- Improve channel/guild fallback in resolved interaction data, using :class:`PartialMessageable` for unhandled/unknown channels instead of using ``None``. (:issue:`646`)
- Check the type of the provided parameter when validating names to improve end-user errors when passing an incorrect object to slash command and option names. (:issue:`653`)
- Make the :func:`.ext.commands.default_member_permissions` decorator always work in cogs. (:issue:`678`)
- Fix :attr:`Spotify.start`, :attr:`Spotify.end`, :attr:`Spotify.duration` raising :exc:`KeyError` instead of returning ``None``, improve activity typing. (:issue:`685`)
- Fixes message initialization failing with threads and no intents by explicitly checking we have a guild object where one is required. (:issue:`699`, :issue:`712`)
- Fixed an issue where it would be possible to remove other features when enabling or disabling the ``COMMUNITY`` feature for a :class:`.Guild`. (:issue:`705`)
- Fix invalid widget fields. (:issue:`736`)
    - :attr:`Widget.invite_url` and :attr:`Widget.fetch_invite` are now optional.
    - :attr:`WidgetMember.avatar` and :attr:`WidgetMember.activity` now work properly and no longer always raise an exception or return ``None``.
- No longer use deprecated `@!` syntax for mentioning users. (:issue:`743`)
- Fix creation of forum threads without :class:`Permissions.manage_threads`. (:issue:`746`)
- Don't count initial message in forum threads towards :attr:`Thread.message_count` and :attr:`Thread.total_message_sent`. (:issue:`747`)
- |commands| Handle :class:`.VoiceChannel` in :func:`commands.is_nsfw`. (:issue:`536`)
- |commands| Handle ``Union[User, Member]`` annotations on slash commands arguments when using the decorator interface. (:issue:`584`)
- |commands| Change :func:`has_permissions <ext.commands.has_permissions>` and :func:`bot_has_permissions <ext.commands.bot_has_permissions>` checks to work with interations in guilds that only added the ``applications.commands`` scope, and in DMs. (:issue:`673`)
- |commands| Fix edge case with parsing command annotations that contain a union of non-type objects, like ``Optional[Literal[1, 2, 3]]``. (:issue:`770`)

Documentation
~~~~~~~~~~~~~

- Add sidebar-navigable sub-sections to Event Reference section of API Reference documentation. (:issue:`460`)
- Remove notes that global application command rollout takes up to an hour. (:issue:`518`)
- Update sphinx from 4.4.0 to version 5.1, and take advantage of new options. (:issue:`522`, :issue:`565`)
- Update the requests intersphinx url to the new url of the requests documentation. (:issue:`539`)
- Build an htmlzip version of the documentation for downloading. (:issue:`541`)
- Fix broken :class:`~ext.commands.Range` references. (:issue:`542`)
- Expand and complete the attribute documentation for :class:`AuditLogDiff`. (:issue:`546`)
- Add note about currently required client override for slash localisations. (:issue:`553`)
- Restructure the ``examples/`` directory, and update + clean up all examples. (:issue:`562`, :issue:`716`)
- Clarify vanity invite handling in :attr:`Guild.invites`. (:issue:`576`)
- Clarify the targets of :func:`Permissions.is_strict_subset` and :func:`Permissions.is_strict_superset`. (:issue:`612`)
- Clarify when the user is a :class:`Member` or a :class:`User` in :func:`disnake.on_member_ban` events. (:issue:`623`)
- Update :attr:`InteractionReference.name` description, now includes group and subcommand. (:issue:`625`, :issue:`648`)
- Note that :attr:`Interaction.channel` may be a :class:`PartialMessageable` in inaccessible threads, in addition to DMs. (:issue:`632`)
- Fix the grammatical errors in :class:`Guild` channel properties. (:issue:`645`)
- Update fields listed in :func:`on_user_update` and :func:`on_member_update` docs. (:issue:`671`)
- Add previously missing inherited attributes to activity types. (:issue:`685`)
- Add documentation for the ``strict`` parameter to :func:`Client.get_or_fetch_user` and :func:`Guild.get_or_fetch_member`. (:issue:`710`)
- Remove note about application command localization requiring a client build override. (:issue:`711`)
- Change references to public guilds to reference the ``COMMUNITY`` feature instead. (:issue:`720`)
- Clarify :func:`Thread.delete` criteria for threads in forum channels. (:issue:`745`)
- Clarify behavior of kwargs in flag methods when both a flag and an alias are given. (:issue:`749`)
- |commands| Document the ``i18n`` attribute on :class:`.ext.commands.Bot` and :class:`.ext.commands.InteractionBot` classes. (:issue:`652`)
- |commands| Document :class:`commands.Injection <ext.commands.Injection>`. (:issue:`669`)
- |commands| Improve documentation around using ``None`` for :attr:`Bot.command_prefix <disnake.ext.commands.Bot.command_prefix>`. (:issue:`689`)

Miscellaneous
~~~~~~~~~~~~~

- Refactor the test bot to be easier to use for all users. (:issue:`247`)
- Refactor channel edit overloads and internals, improving typing. (:issue:`418`)
- Run pyright on examples and fix any typing issues uncovered by this change. (:issue:`519`)
- Add initial testing framework. (:issue:`529`)
- Explicitly type activity types with literal return values. (:issue:`543`)
- Explicitly type channel types with literal return values. (:issue:`543`)
- Update PyPI url and minor wording in the README. (:issue:`556`)
- Add ``flake8`` as our linter. (:issue:`557`)
- Update pyright to 1.1.254. (:issue:`559`)
- Add generic parameters to user/message command decorators. (:issue:`563`)
    - Update default parameter type to improve compatibilty with callable/dynamic defaults.
- Run docs creation in GitHub actions to test for warnings before a pull is merged. (:issue:`564`)
- Add more typing overrides to :class:`GuildCommandInteraction`. (:issue:`580`)
- Rework internal typings for interaction payloads. (:issue:`588`)
- Add typings for all gateway payloads. (:issue:`594`)
- Add ``towncrier`` and ``sphinxcontrib-towncrier`` to manage changelogs. (:issue:`600`)
    - Use ``towncrier`` for changelog management.
    - Use ``sphinxcontrib-towncrier`` to build changelogs for the in-development documentation.
- Expand contributing documentation to include more information on creating pull requests and writing features. (:issue:`601`)
- Add flake8-comprehensions for catching inefficient comphrehensions. (:issue:`602`)
- Resolve minor flake8 issues. (:issue:`606`)
    - Don't use star imports except in ``__init__.py`` files.
    - Don't use ambigious variable names.
    - Don't use setattr and getattr with constant variable names.
- Add ``flake8-pytest-style`` for linting pytest specific features with flake8. (:issue:`608`)
- Replace all :class:`TypeVar` instances with ``typing_extensions.Self`` across the entire library where possible. (:issue:`610`)
- Remove the internal ``fill_with_flags`` decorator for flags classes and use the built in :meth:`object.__init_subclass__` method. (:issue:`616`, :issue:`660`)
- Add :class:`slice` to :class:`.ui.ActionRow` ``__getattr__`` and ``__delattr__`` annotations. (:issue:`624`)
- Update and standardise all internal Snowflake regexes to match between 17 and 19 characters (inclusive). (:issue:`651`)
- Rename internal module ``disnake.ext.commands.flags`` to ``disnake.ext.commands.flag_converter``. (:issue:`667`)
- Improve parallel documentation build speed. (:issue:`690`)
- Limit installation of ``cchardet`` in the ``[speed]`` extra to Python versions below 3.10 (see `aiohttp#6857 <https://github.com/aio-libs/aiohttp/pull/6857>`__). (:issue:`702`)
- Update annotation and description of ``options`` parameter of :func:`ui.ActionRow.add_select <disnake.ui.ActionRow.add_select>` to match :class:`ui.Select <disnake.ui.Select>`. (:issue:`744`)
- Update typings to explicitly specify optional types for parameters with a ``None`` default. (:issue:`751`)
- Adopt `SPDX License Headers <https://spdx.dev/ids>`_ across all project files. (:issue:`756`)

.. _vp2p5p3:

v2.5.3
------

This is a maintenance release with backports from v2.6.0.

Bug Fixes
~~~~~~~~~

- Fix creation of forum threads without :class:`Permissions.manage_threads`. (:issue:`746`)
- |commands| Fix edge case with parsing command annotations that contain a union of non-type objects, like ``Optional[Literal[1, 2, 3]]``. (:issue:`771`)

Miscellaneous
~~~~~~~~~~~~~

- Limit installation of ``cchardet`` in the ``[speed]`` extra to Python versions below 3.10 (see `aiohttp#6857 <https://github.com/aio-libs/aiohttp/pull/6857>`__). (:issue:`772`)

.. _vp2p5p2:

v2.5.2
------

This release is a bugfix release with backports from upto v2.6.0.

Bug Fixes
~~~~~~~~~

- Warn the user that bools are not supported for ``default_member_permissions``. (:issue:`520`)
- Update the Guild Iterator to not get stuck in an infinite loop. (:issue:`526`)
    - Add a missing import for the scheduled event user iterator.
- Change the default guild :class:`.GuildSticker` limit to 5. (:issue:`531`)
- Handle optional :class:`Locale` instances (no longer create an enum value). (:issue:`533`)
- |commands| Handle :class:`.VoiceChannel` in :func:`commands.is_nsfw`. (:issue:`536`)
- Dispatch :func:`disnake.on_reaction_remove` for :class:`.Thread` instances. (:issue:`536`)
- Update :attr:`Guild.bitrate_limit` to use the correct value for the ``VIP_REGIONS`` feature flag. (:issue:`538`)
- Make all \*InteractionData dataclasses dicts (:class:`MessageInteractionData`, :class:`ApplicationCommandInteractionData`, and so on). (:issue:`549`)
- Handle :class:`ThreadAutoArchiveDuration` instances for ``default_auto_archive_duration`` when editing channels. (:issue:`568`)
- Assume that ``None`` is an empty channel name and keep ``channel.name`` a string. (:issue:`569`)
- Remove the ``$`` prefix from ``IDENTIFY`` payload properties. (:issue:`572`)
- Replace old application command objects in cogs with the new/copied objects. (:issue:`575`)
- |commands| Handle ``Union[User, Member]`` annotations on slash commands arguments when using the decorator interface. (:issue:`584`)
- Fix opus function calls on arm64 macOS. (:issue:`620`)
- Improve channel/guild fallback in resolved interaction data, using :class:`PartialMessageable` for unhandled/unknown channels instead of using ``None``. (:issue:`646`)

Documentation
~~~~~~~~~~~~~

- Remove notes that global application command rollout takes up to an hour. (:issue:`518`)
- Update the requests intersphinx url to the new url of the requests documentation. (:issue:`539`)
- Clarify the targets of :func:`Permissions.is_strict_subset` and :func:`Permissions.is_strict_superset`. (:issue:`612`)
- Update :attr:`InteractionReference.name` description, now includes group and subcommand. (:issue:`625`, :issue:`648`)

.. _vp2p5p1:

v2.5.1
------

Bug Fixes
~~~~~~~~~

- |commands| Fix :func:`~ext.commands.InvokableSlashCommand.autocomplete` decorator in cogs (:issue:`521`)

.. _vp2p5p0:

v2.5.0
------

This version adds support for **API v10** (which comes with a few breaking changes),
**forum channels**, **localizations**, **permissions v2**, improves API coverage by adding support for previously
missing features like guild previews, widgets, or welcome screens,
and contains several miscellaneous enhancements and bugfixes.

Regarding the message content intent:
Note that earlier versions will continue working fine after the message content intent deadline (August 31st 2022),
as long as the intent is enabled in the developer portal. However, from this version (``2.5.0``) onward, the intent needs to be
enabled in the developer portal *and* your code.
See `this page <https://guide.disnake.dev/popular-topics/intents#why-do-most-messages-have-no-content>`_ of the guide for more information.
If you do not have access to the intent yet, you can temporarily continue using API v9 by calling ``disnake.http._workaround_set_api_version(9)`` before connecting,
which will keep sending message content before the intent deadline, even with the intent disabled.

Breaking Changes
~~~~~~~~~~~~~~~~

- The :attr:`~Intents.message_content` intent is now required to receive message content and related fields, see above (:issue:`353`)
- The new permissions v2 system revamped application command permissions, with the most notable changes being the
  removal of ``default_permission`` and ``commands.guild_permissions`` in favor of new fields/methods - see below for all new changes (:issue:`405`)
- :func:`TextChannel.create_thread` now requires either a ``message`` or a ``type`` parameter (:issue:`355`)
- :func:`GuildScheduledEvent.fetch_users` and :func:`Guild.bans` now return an async iterator instead of a list of users (:issue:`428`, :issue:`442`)
- :func:`Guild.audit_logs` no longer supports the ``oldest_first`` parameter (:issue:`473`)
- Store channels have been removed as they're not supported by Discord any longer (:issue:`438`)
- :func:`on_thread_join` will no longer be invoked when a new thread is created, see :func:`on_thread_create` (:issue:`445`)
- The voice region enum was replaced with a generic :class:`VoiceRegion` data class (:issue:`477`)
- ``locale`` attributes are now of type :class:`Locale` instead of :class:`str` (:issue:`439`)
- ``Invite.revoked`` and ``Thread.archiver_id`` have been removed (deprecated in 2.4) (:issue:`455`)
- Slash command names and option names are no longer automatically converted to lowercase, an :class:`InvalidArgument` exception is now raised instead (:issue:`422`)
- The ``interaction`` parameter of :func:`ui.Item.callback` can no longer be passed as a kwarg (:issue:`311`)
- The ``youtube``, ``awkword`` and ``sketchy_artist`` :class:`PartyType`\s no longer work and have been removed (:issue:`408`, :issue:`409`)
- Trying to defer an interaction response that does not support deferring (e.g. autocomplete) will now raise a :class:`TypeError` (:issue:`505`)
- |commands| Failure to convert an input parameter annotated as :class:`~ext.commands.LargeInt` now
  raises a :exc:`~ext.commands.LargeIntConversionFailure` (:issue:`362`)


Deprecations
~~~~~~~~~~~~

- Public stages and stage discoverability are deprecated and no longer supported (:issue:`287`)
- Voice regions on guild level are deprecated and no longer have any effect;
  they should be set on a per-channel basis instead (:issue:`357`, :issue:`374`)
- :func:`Guild.create_integration`, :func:`Integration.delete`, :func:`StreamIntegration.edit` and :func:`StreamIntegration.sync`
  can't be used by bots anymore and will be removed in a future version (:issue:`361`)
- :attr:`AppInfo.summary`, :attr:`PartialAppInfo.summary` and :attr:`IntegrationApplication.summary` are deprecated, use ``.description`` instead (:issue:`369`)
- The ``suppress`` parameter for edit methods has been deprecated in favor of ``suppress_embeds``, with unchanged functionality (:issue:`474`)


New Features
~~~~~~~~~~~~

- Support API v10 (:issue:`353`)
    - New intent: :attr:`Intents.message_content`
    - |commands| New warning: :class:`~ext.commands.MessageContentPrefixWarning`
- Add forum channels (:issue:`448`, :issue:`479`, :issue:`504`, :issue:`512`)
    - Add :class:`ForumChannel`
    - Add :attr:`CategoryChannel.forum_channels`, :attr:`Guild.forum_channels`
    - Add :attr:`CategoryChannel.create_forum_channel`, :attr:`Guild.create_forum_channel`
    - Add :class:`ChannelFlags`, :attr:`Thread.flags`, :attr:`Thread.is_pinned`
    - Add ``pinned`` parameter to :func:`Thread.edit`
    - Add :attr:`Permissions.create_forum_threads`, alias of :attr:`~Permissions.send_messages`
    - |commands| Add :class:`~ext.commands.ForumChannelConverter`
- Add application command localizations, see :ref:`localizations` (:issue:`269`)
    - Add :class:`Localized`, :class:`LocalizationProtocol`, :class:`LocalizationStore`
    - Most ``name`` and ``description`` parameters now also accept a :class:`Localized` object
    - Update docstring parsing to accommodate for localizations
    - Add :attr:`Client.i18n`
    - Add ``localization_provider`` and ``strict_localization`` parameters to :class:`Client`
    - Add ``with_localizations`` parameter to :func:`Client.fetch_global_commands`, :func:`Client.fetch_guild_commands`
    - Add :class:`LocalizationWarning`, :class:`LocalizationKeyError`
    - Add :func:`utils.as_valid_locale`
    - Add localization example
- Support permissions v2, see :ref:`app_command_permissions` (:issue:`405`)
    - Breaking changes:
        - Remove support for ``default_permission``
        - Remove :func:`GuildApplicationCommandPermissions.edit`, :class:`PartialGuildApplicationCommandPermissions`, :class:`UnresolvedGuildApplicationCommandPermissions`
        - Remove :func:`Client.edit_command_permissions`, :func:`Client.bulk_edit_command_permissions`, :func:`Client.edit_command_permissions`, :func:`Client.edit_command_permissions`
        - Remove :func:`Guild.get_command_permissions`, :func:`Guild.edit_command_permissions`, :func:`Guild.bulk_edit_command_permissions`
        - Update behavior of :class:`GuildCommandInteraction` annotation to automatically set ``dm_permission=False`` instead of adding a local check, remove support for subcommands
        - Add :class:`ApplicationCommandPermissionType` enum, change type of :attr:`ApplicationCommandPermissions.type` to support channel targets
        - |commands| Remove :func:`~ext.commands.guild_permissions` decorator
        - |commands| Remove ``sync_permissions`` parameter from :class:`~ext.commands.Bot`
    - New features:
        - Add ``dm_permission`` and ``default_member_permissions`` parameters to application command objects and decorators
        - Add :attr:`~ApplicationCommand.dm_permission`, :attr:`~ApplicationCommand.default_member_permissions` attributes
          to :class:`ApplicationCommand` and :class:`~ext.commands.InvokableApplicationCommand`
        - Add :func:`ApplicationCommandPermissions.is_everyone` and :func:`ApplicationCommandPermissions.is_all_channels`
        - Add :attr:`AuditLogAction.application_command_permission_update` enum value and :attr:`AuditLogDiff.command_permissions`
        - Add :func:`on_application_command_permissions_update` event
        - |commands| Add :func:`~ext.commands.default_member_permissions` decorator, alternative to identically named parameter
- Add guild previews (:issue:`359`)
    - Add :class:`GuildPreview`
    - Add :func:`Client.fetch_guild_preview`
- Add guild widget settings and widget url (:issue:`360`, :issue:`365`)
    - Add :class:`WidgetSettings`, :class:`WidgetStyle`
    - Add :func:`Guild.widget_settings`, :func:`Guild.widget_image_url`
    - Add :func:`Widget.image_url`
    - Change :func:`Guild.edit_widget` return type
- Add guild welcome screens (:issue:`339`)
    - Add :class:`WelcomeScreen`, :class:`WelcomeScreenChannel`
    - Add :func:`Guild.welcome_screen`, :func:`Guild.edit_welcome_screen`
    - Add :attr:`Invite.guild_welcome_screen`

- Support ``List[str]`` and ``Dict[str, str]`` in ``option`` parameter of :class:`disnake.ui.Select` (:issue:`326`)
- Add :func:`Guild.search_members` (:issue:`358`, :issue:`388`)
- Add :attr:`ModalInteraction.message` (:issue:`363`, :issue:`400`)
- Support :func:`InteractionResponse.edit_message` for modal interactions, if modal was sent in response to component interaction (:issue:`364`, :issue:`400`)
- Support ``reason`` parameter in :func:`Message.create_thread` and :func:`Thread.delete` (:issue:`366`)
- Add :attr:`StageInstance.guild_scheduled_event` and :attr:`StageInstance.guild_scheduled_event_id` (:issue:`394`)
- Add :class:`SessionStartLimit` and :attr:`Client.session_start_limit` (:issue:`402`)
- Add :attr:`PartialInviteGuild.premium_subscription_count` (:issue:`410`)
- Allow passing asset types for most image parameters, in addition to :class:`bytes` (:issue:`415`)
- Update :func:`GuildScheduledEvent.fetch_users` and :func:`Guild.bans` to be async iterators supporting pagination (:issue:`428`, :issue:`442`)
- Add :attr:`AuditLogDiff.image` for scheduled event images (:issue:`432`)
- Add :class:`Locale` enum (:issue:`439`)
- Add ``notify_everyone`` parameter to :func:`StageChannel.create_instance` (:issue:`440`)
- Add :func:`~Asset.to_file` method to assets, emojis, stickers (:issue:`443`, :issue:`475`)
- Add :func:`on_thread_create` event (:issue:`445`)
- Support ``reason`` parameter in :func:`Thread.edit` (:issue:`454`)
- Add ``default_auto_archive_duration`` parameter to :func:`Guild.create_text_channel`, add ``nsfw`` parameter to :func:`Guild.create_voice_channel` (:issue:`456`)
- Allow providing ``attachments=None`` to clear attachments when editing a message (:issue:`457`)
- Add ``__repr__`` methods to interaction data types (:issue:`458`)
- Add :func:`VoiceChannel.delete_messages`, :func:`VoiceChannel.purge`, :func:`VoiceChannel.webhooks`, :func:`VoiceChannel.create_webhook`, and improve :func:`VoiceChannel.permissions_for` (:issue:`461`)
- Add :attr:`AppInfo.tags`, :attr:`AppInfo.install_params`, :attr:`AppInfo.custom_install_url` (:issue:`463`)
- Add :attr:`TextChannel.last_pin_timestamp`, :attr:`DMChannel.last_pin_timestamp`, :attr:`Thread.last_pin_timestamp` (:issue:`464`)
- Add :attr:`MessageType.auto_moderation_action` (:issue:`465`)
- Add temporary workaround for setting API version to avoid message content intent requirement until deadline (:issue:`467`)
- Add :attr:`Interaction.expires_at` and :attr:`Interaction.is_expired`, automatically fall back to message edit/delete if interaction expired (:issue:`469`)
- Add ``suppress_embeds`` parameter to message send methods (:issue:`474`)
- Add :class:`VoiceRegion` (replacing voice region enum), :func:`Client.fetch_voice_regions`, :func:`Guild.fetch_voice_regions` (:issue:`477`)
- Add :attr:`Member.role_icon` property (:issue:`485`)
- Add debug logging of webhook request/response data (:issue:`486`)
- Add :func:`on_raw_thread_delete`, :func:`on_raw_thread_member_remove` and :func:`on_raw_thread_update` events (:issue:`495`)
- Support creating news channels using :func:`Guild.create_text_channel` (:issue:`497`)
- Add :attr:`Guild.vanity_url_code`, add option to :func:`Guild.vanity_invite` to use cached invite code (:issue:`502`)
- Add :attr:`Message.application_id` (:issue:`513`)
- |commands| Add :class:`~ext.commands.GuildScheduledEventConverter` and :exc:`~ext.commands.GuildScheduledEventNotFound` (:issue:`376`)
- |commands| Add :attr:`~ext.commands.InvokableApplicationCommand.extras` to application commands (:issue:`483`)
- |commands| Add ``slash_command_attrs``, ``user_command_attrs`` and ``message_command_attrs`` :class:`~ext.commands.Cog` parameters (:issue:`501`)

Bug Fixes
~~~~~~~~~

- Improve components exception message (:issue:`352`)
- Use proper HTTP method for joining threads, remove unused methods (:issue:`356`)
- Fix missing ``create_public_threads`` permission in :attr:`Permissions.private_channel` (:issue:`373`)
- Ensure token is of type :class:`str` (:issue:`375`)
- Improve :func:`abc.Messageable.send` typing and fix annotations of HTTP methods (:issue:`378`)
- Fix shadowed ``disnake.message`` module (:issue:`380`)
- Fix missing/incorrect ``__slots__`` (:issue:`381`)
- Fix :attr:`PartialInviteChannel.__str__ <PartialInviteChannel>` (:issue:`383`)
- Fix role icon/emoji editing (:issue:`403`)
- Remove cached scheduled events if associated channel was deleted (:issue:`406`)
- Update some types/parameters of roles, scheduled events and voice states (:issue:`407`)
- Allow ``content`` parameters in send/edit methods to be positional (:issue:`411`)
- Fix gateway ratelimiter being too strict (:issue:`413`)
- Fix caching of stage instances andd scheduled events (:issue:`416`)
- Fix memory leaks on shard reconnect (:issue:`424`, :issue:`425`)
- Improve :class:`PartialMessageable` channel handling (:issue:`426`)
- Use :func:`asyncio.iscoroutinefunction` instead of :func:`inspect.iscoroutinefunction` (:issue:`427`)
- Fix :func:`~PartialEmoji.read` for activity emojis (:issue:`430`)
- Don't automatically enable logging if autoreload is enabled (:issue:`431`)
- Support embed images in :func:`InteractionResponse.edit_message` (:issue:`466`)
- Fix ``after`` parameter of :func:`Guild.audit_logs` (:issue:`473`)
- Add ``__str__`` to :class:`ApplicationCommand`, improve sync debug output (:issue:`478`)
- Don't require a ``topic`` when creating a stage channel (:issue:`480`)
- Update and add missing overloads (:issue:`482`)
- Make ``disnake.types.interactions`` importable at runtime (:issue:`493`)
- Raise :class:`TypeError` instead of silently returning when trying to defer an unsupported interaction type (:issue:`505`)
- Fix delay of ``after`` callback in :class:`AudioPlayer` when stopping (:issue:`508`)
- |commands| Make conversion exceptions in slash commands propagate cleanly as documented (:issue:`362`)
- |commands| Fix :class:`~ext.commands.clean_content` converter (:issue:`396`)
- |commands| Fix usage of custom converters with :func:`Param <ext.commands.Param>` (:issue:`398`)
- |commands| Support interactions in :class:`~ext.commands.UserConverter`, :class:`~ext.commands.MemberConverter` (:issue:`429`)
- |commands| Fix unloading of listeners with custom names (:issue:`444`)
- |commands| Fix parameter name conflicts in slash commands (:issue:`503`)

Documentation
~~~~~~~~~~~~~

- Disable mathjax in documentation to improve loading times (:issue:`370`)
- Update return type of :func:`Guild.create_template` (:issue:`372`)
- Add documentation for :class:`GuildCommandInteraction`, :class:`UserCommandInteraction`, and :class:`MessageCommandInteraction` (:issue:`374`)
- Fix several bugs of redesign (:issue:`377`)
- Update broken references (:issue:`419`)
- Fix duplicate search results, improve scoring (:issue:`423`)
- Add search hotkeys ``ctrl+k``, ``/``, ``s`` (:issue:`434`)
- Fix string escape warnings (:issue:`436`)
- Add several previously missing documentation entries (:issue:`446`, :issue:`470`)
- Add autocomplete decorator example (:issue:`472`)
- Update docs of ABCs to mention subclasses (:issue:`506`)
- Update :func:`on_member_update` documentation to include new and future attributes (:issue:`510`)
- Fix miscellaneous issues, improve formatting (:issue:`511`)

Miscellaneous
~~~~~~~~~~~~~

- Fix remaining pyright issues, add pyright CI (:issue:`311`, :issue:`387`, :issue:`514`)
- Update dev dependencies and CI (:issue:`345`, :issue:`386`, :issue:`451`)
- Improve ``_WebhookState`` typing (:issue:`391`)
- Improve ``basic_bot.py`` example (:issue:`399`)
- Add low-level component example (:issue:`452`)
- Update Discord server invite links (:issue:`476`)

.. _vp2p4p1:

v2.4.1
------

This release is a bugfix release with backports from v2.5.0 up to v2.5.2.

Bug Fixes
~~~~~~~~~

- Fix missing ``create_public_threads`` permission in :attr:`Permissions.private_channel` (:issue:`373`)
- Fix :attr:`PartialInviteChannel.__str__ <PartialInviteChannel>` (:issue:`383`)
- Fix role icon/emoji editing (:issue:`403`)
- Remove cached scheduled events if associated channel was deleted (:issue:`406`)
- Update some types/parameters of roles, scheduled events and voice states (:issue:`407`)
- Allow ``content`` parameters in send/edit methods to be positional (:issue:`411`)
- Fix gateway ratelimiter being too strict (:issue:`413`)
- Fix caching of stage instances andd scheduled events (:issue:`416`)
- Fix memory leaks on shard reconnect (:issue:`424`, :issue:`425`)
- Improve :class:`PartialMessageable` channel handling (:issue:`426`)
- Fix :func:`~PartialEmoji.read` for activity emojis (:issue:`430`)
- Fix delay of ``after`` callback in :class:`AudioPlayer` when stopping (:issue:`508`)
- Change the default guild :class:`.GuildSticker` limit to 5. (:issue:`531`)
- Dispatch :func:`disnake.on_reaction_remove` for :class:`.Thread` instances. (:issue:`536`)
- Update :attr:`Guild.bitrate_limit` to use the correct value for the ``VIP_REGIONS`` feature flag. (:issue:`538`)
- Remove the ``$`` prefix from ``IDENTIFY`` payload properties. (:issue:`572`)
- Fix opus function calls on arm64 macOS. (:issue:`620`)
- Improve channel/guild fallback in resolved interaction data, using :class:`PartialMessageable` for unhandled/unknown channels instead of using ``None``. (:issue:`646`)
- |commands| Fix :class:`~ext.commands.clean_content` converter (:issue:`396`)
- |commands| Support interactions in :class:`~ext.commands.UserConverter`, :class:`~ext.commands.MemberConverter` (:issue:`429`)
- |commands| Fix unloading of listeners with custom names (:issue:`444`)
- |commands| Handle :class:`.VoiceChannel` in :func:`commands.is_nsfw`. (:issue:`536`)

Documentation
~~~~~~~~~~~~~

- Update the requests intersphinx url to the new url of the requests documentation. (:issue:`539`)

Miscellaneous
~~~~~~~~~~~~~

- Update dev dependencies and CI (:issue:`451`)

.. _vp2p4p0:

v2.4.0
------

This version contains many new features, including attachment options, modals,
and the ability to directly send message components without views,
as well as several fixes and other general improvements.

Breaking Changes
~~~~~~~~~~~~~~~~

- The constructor of :class:`ApplicationCommand` and its subtypes no longer accepts ``**kwargs`` for setting internal values (:issue:`249`)
    - This shouldn't affect anyone, as ``**kwargs`` was only used for setting fields returned by the API and had no effect if the user set them
- :attr:`Interaction.permissions` now returns proper permission values in DMs (:issue:`321`)
- The ``reason`` parameter for sticker endpoints in :class:`HTTPClient` is now kwarg-only

Deprecations
~~~~~~~~~~~~

- :attr:`Thread.archiver_id` is not being provided by the API anymore and will be removed in a future version (:issue:`295`)
- :attr:`Invite.revoked` is not being provided by the API anymore and will be removed in a future version (:issue:`309`)

New Features
~~~~~~~~~~~~

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
~~~~~~~~~

- Fix missing support for ``reason`` parameter in some methods (:issue:`266`)
- Improve validation of slash command and option names (:issue:`267`)
- |commands| Fix typing of ``ctx`` parameter in :class:`~disnake.ext.commands.Converter` (:issue:`292`)
- Fix :func:`Guild.get_command` never returning any commands (:issue:`333`)
- Return list of members from :func:`Guild.chunk` (:issue:`334`)
- Fix handling of uppercase slash command names (:issue:`346`)
- Fix ``permissions`` annotation of :func:`abc.GuildChannel.set_permissions` (:issue:`349`)
- Fix :func:`tasks.loop <disnake.ext.tasks.loop>` usage with fixed times (:issue:`337`)

Documentation
~~~~~~~~~~~~~

- Show tooltips when hovering over links (:issue:`236`, :issue:`242`)
- General content improvements/adjustments (:issue:`275`)
- Slight redesign and general layout improvements (:issue:`278`)

Miscellaneous
~~~~~~~~~~~~~

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
------

This version contains several new features and fixes,
notably support for guild scheduled events, guild timeouts,
and a slash command rework with parameter injections, as well as several documentation fixes.

Note: the :ref:`version_guarantees` have been updated to more accurately reflect the versioning scheme this library is following.

Breaking Changes
~~~~~~~~~~~~~~~~

- The supported aiohttp version range changed from ``>=3.6.0,<3.8.0`` to ``>=3.7.0,<3.9.0``
- Due to the upcoming text-in-voice feature (not yet released at the time of writing),
  many methods/properties that previously returned a :class:`TextChannel` can now also return a :class:`VoiceChannel`, which shares many but not all of its methods.
  Also see the details for text-in-voice under "New Features" below, which include a few important things to note.
- Slash command internals have undergone an extensive rework, and while existing code should still work as before, it is recommended that you do some testing using the new implementation first
- :func:`Bot.get_slash_command <ext.commands.Bot.get_slash_command>` may now also return :class:`SubCommandGroup <ext.commands.SubCommandGroup>` or :class:`SubCommand <ext.commands.SubCommand>` instances, see documentation
- ``disnake.types.ThreadArchiveDuration`` is now ``ThreadArchiveDurationLiteral``, to avoid confusion with the new :class:`ThreadArchiveDuration` enum

Deprecations
~~~~~~~~~~~~

- The ``role_ids`` and ``user_ids`` parameters for :func:`guild_permissions <ext.commands.guild_permissions>` are now
  ``roles`` and ``users`` respectively; the old parameter names will be removed in a future version

New Features
~~~~~~~~~~~~

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
- |commands| Add parameter injections (`example <https://github.com/DisnakeDev/disnake/blob/master/examples/interactions/injections.py>`__) (:issue:`130`)
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
~~~~~~~~~

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
~~~~~~~~~~~~~

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
~~~~~~~~~~~~~

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
------

Bug Fixes
~~~~~~~~~

- Fix channel conversion in audit log entries
- Fix improper error handling in context menu commands
- Supply :attr:`ApplicationCommandInteraction.application_command` in autocomplete callbacks
- Fix :class:`Select.append_option <disnake.ui.Select.append_option>` not raising an error if 25 options have already been added
- Improve check for ``options`` parameter on slash commands and subcommands
- Improve parameter parsing for converters
- Fix warning related to new option properties

Documentation
~~~~~~~~~~~~~

- Update repository links to new organization
- Fix duplicate entries in documentation
- Fix incorrect ``versionadded`` tags
- Add documentation for :class:`InteractionBot <ext.commands.InteractionBot>` and :class:`AutoShardedInteractionBot <ext.commands.AutoShardedInteractionBot>`

.. _vp2p2p1:

v2.2.1
------

Bug Fixes
~~~~~~~~~

- Fixed error related to guild member count

.. _vp2p2p0:

v2.2.0
------

New Features
~~~~~~~~~~~~

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
------

New Features
~~~~~~~~~~~~

- Add :class:`InteractionReference`
- Add :class:`UnresolvedGuildApplicationCommandPermissions`
- Add :attr:`Message.interaction`
- Add kwargs ``min_value`` and ``max_value`` in :class:`Option`
- |commands| Add kwarg ``min_value`` (with aliases ``ge``, ``gt``) to :func:`Param <ext.commands.Param>`
- |commands| Add kwarg ``max_value`` (with aliases ``le``, ``lt``) to :func:`Param <ext.commands.Param>`
- |commands| Add kwarg ``owner`` to :func:`guild_permissions <ext.commands.guild_permissions>`

Bug Fixes
~~~~~~~~~

- Command deletions on reconnections
- Pending sync tasks on loop termination

.. _vp2p1p4:

v2.1.4
------

Bug Fixes
~~~~~~~~~

- Fixed some issues with application command permissions synchronisation

.. _vp2p1p3:

v2.1.3
------

New Features
~~~~~~~~~~~~

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
~~~~~~~~~

- Music
- ``default_permission`` kwarg in user / message commands
- Commands no longer sync during the loop termination

.. _vp2p1p2:

v2.1.2
------

This is the first stable version of this discord.py 2.0 fork.

New Features
~~~~~~~~~~~~

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


Legacy Changelog
----------------

Changelogs for older versions (``0.x``, ``1.x``) can be found on the :ref:`whats_new_legacy` page.
