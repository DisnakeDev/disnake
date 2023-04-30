# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Dict, List, Tuple

from .enums import Event


class EventData:
    def __init__(
        self,
        *,
        type_args: List[str],
        bot: bool = False,
        event_only: bool = False,
    ) -> None:
        self.type_args: Tuple[str, ...] = tuple(type_args)
        """Type names of event arguments, e.g. `("Guild", "User")`"""

        self.bot: bool = bot
        """Whether the event is specific to ext.commands"""

        self.event_only: bool = event_only
        """Whether the event can only be used through `@event` and not other listeners"""


EVENT_DATA: Dict[Event, EventData] = {
    Event.connect: EventData(
        type_args=[],
    ),
    Event.disconnect: EventData(
        type_args=[],
    ),
    # FIXME: figure out how to specify varargs for these two if we ever add overloads for @event
    Event.error: EventData(
        type_args=[],
        event_only=True,
    ),
    Event.gateway_error: EventData(
        type_args=[],
        event_only=True,
    ),
    Event.ready: EventData(
        type_args=[],
    ),
    Event.resumed: EventData(
        type_args=[],
    ),
    Event.shard_connect: EventData(
        type_args=["int"],
    ),
    Event.shard_disconnect: EventData(
        type_args=["int"],
    ),
    Event.shard_ready: EventData(
        type_args=["int"],
    ),
    Event.shard_resumed: EventData(
        type_args=["int"],
    ),
    Event.socket_event_type: EventData(
        type_args=["str"],
    ),
    Event.socket_raw_receive: EventData(
        type_args=["str"],
    ),
    Event.socket_raw_send: EventData(
        type_args=["Union[str, bytes]"],
    ),
    Event.guild_channel_create: EventData(
        type_args=["GuildChannel"],
    ),
    Event.guild_channel_update: EventData(
        type_args=["GuildChannel", "GuildChannel"],
    ),
    Event.guild_channel_delete: EventData(
        type_args=["GuildChannel"],
    ),
    Event.guild_channel_pins_update: EventData(
        type_args=["Union[GuildChannel, Thread]", "Optional[datetime]"],
    ),
    Event.invite_create: EventData(
        type_args=["Invite"],
    ),
    Event.invite_delete: EventData(
        type_args=["Invite"],
    ),
    Event.private_channel_update: EventData(
        type_args=["GroupChannel", "GroupChannel"],
    ),
    Event.private_channel_pins_update: EventData(
        type_args=["PrivateChannel", "Optional[datetime]"],
    ),
    Event.webhooks_update: EventData(
        type_args=["GuildChannel"],
    ),
    Event.thread_create: EventData(
        type_args=["Thread"],
    ),
    Event.thread_update: EventData(
        type_args=["Thread", "Thread"],
    ),
    Event.thread_delete: EventData(
        type_args=["Thread"],
    ),
    Event.thread_join: EventData(
        type_args=["Thread"],
    ),
    Event.thread_remove: EventData(
        type_args=["Thread"],
    ),
    Event.thread_member_join: EventData(
        type_args=["ThreadMember"],
    ),
    Event.thread_member_remove: EventData(
        type_args=["ThreadMember"],
    ),
    Event.raw_thread_member_remove: EventData(
        type_args=["RawThreadMemberRemoveEvent"],
    ),
    Event.raw_thread_update: EventData(
        type_args=["Thread"],
    ),
    Event.raw_thread_delete: EventData(
        type_args=["RawThreadDeleteEvent"],
    ),
    Event.guild_join: EventData(
        type_args=["Guild"],
    ),
    Event.guild_remove: EventData(
        type_args=["Guild"],
    ),
    Event.guild_update: EventData(
        type_args=["Guild", "Guild"],
    ),
    Event.guild_available: EventData(
        type_args=["Guild"],
    ),
    Event.guild_unavailable: EventData(
        type_args=["Guild"],
    ),
    Event.guild_role_create: EventData(
        type_args=["Role"],
    ),
    Event.guild_role_delete: EventData(
        type_args=["Role"],
    ),
    Event.guild_role_update: EventData(
        type_args=["Role", "Role"],
    ),
    Event.guild_emojis_update: EventData(
        type_args=["Guild", "Sequence[Emoji]", "Sequence[Emoji]"],
    ),
    Event.guild_stickers_update: EventData(
        type_args=["Guild", "Sequence[GuildSticker]", "Sequence[GuildSticker]"],
    ),
    Event.guild_integrations_update: EventData(
        type_args=["Guild"],
    ),
    Event.guild_scheduled_event_create: EventData(
        type_args=["GuildScheduledEvent"],
    ),
    Event.guild_scheduled_event_update: EventData(
        type_args=["GuildScheduledEvent", "GuildScheduledEvent"],
    ),
    Event.guild_scheduled_event_delete: EventData(
        type_args=["GuildScheduledEvent"],
    ),
    Event.guild_scheduled_event_subscribe: EventData(
        type_args=["GuildScheduledEvent", "Union[Member, User]"],
    ),
    Event.guild_scheduled_event_unsubscribe: EventData(
        type_args=["GuildScheduledEvent", "Union[Member, User]"],
    ),
    Event.raw_guild_scheduled_event_subscribe: EventData(
        type_args=["RawGuildScheduledEventUserActionEvent"],
    ),
    Event.raw_guild_scheduled_event_unsubscribe: EventData(
        type_args=["RawGuildScheduledEventUserActionEvent"],
    ),
    Event.application_command_permissions_update: EventData(
        type_args=["GuildApplicationCommandPermissions"],
    ),
    Event.automod_action_execution: EventData(
        type_args=["AutoModActionExecution"],
    ),
    Event.automod_rule_create: EventData(
        type_args=["AutoModRule"],
    ),
    Event.automod_rule_update: EventData(
        type_args=["AutoModRule"],
    ),
    Event.automod_rule_delete: EventData(
        type_args=["AutoModRule"],
    ),
    Event.audit_log_entry_create: EventData(
        type_args=["AuditLogEntry"],
    ),
    Event.integration_create: EventData(
        type_args=["Integration"],
    ),
    Event.integration_update: EventData(
        type_args=["Integration"],
    ),
    Event.raw_integration_delete: EventData(
        type_args=["RawIntegrationDeleteEvent"],
    ),
    Event.member_join: EventData(
        type_args=["Member"],
    ),
    Event.member_remove: EventData(
        type_args=["Member"],
    ),
    Event.member_update: EventData(
        type_args=["Member", "Member"],
    ),
    Event.raw_member_remove: EventData(
        type_args=["RawGuildMemberRemoveEvent"],
    ),
    Event.raw_member_update: EventData(
        type_args=["Member"],
    ),
    Event.member_ban: EventData(
        type_args=["Guild", "Union[User, Member]"],
    ),
    Event.member_unban: EventData(
        type_args=["Guild", "User"],
    ),
    Event.presence_update: EventData(
        type_args=["Member", "Member"],
    ),
    Event.user_update: EventData(
        type_args=["User", "User"],
    ),
    Event.voice_state_update: EventData(
        type_args=["Member", "VoiceState", "VoiceState"],
    ),
    Event.stage_instance_create: EventData(
        type_args=["StageInstance"],
    ),
    Event.stage_instance_delete: EventData(
        type_args=["StageInstance", "StageInstance"],
    ),
    Event.stage_instance_update: EventData(
        type_args=["StageInstance"],
    ),
    Event.application_command: EventData(
        type_args=["ApplicationCommandInteraction"],
    ),
    Event.application_command_autocomplete: EventData(
        type_args=["ApplicationCommandInteraction"],
    ),
    Event.button_click: EventData(
        type_args=["MessageInteraction"],
    ),
    Event.dropdown: EventData(
        type_args=["MessageInteraction"],
    ),
    Event.interaction: EventData(
        type_args=["Interaction"],
    ),
    Event.message_interaction: EventData(
        type_args=["MessageInteraction"],
    ),
    Event.modal_submit: EventData(
        type_args=["ModalInteraction"],
    ),
    Event.message: EventData(
        type_args=["Message"],
    ),
    Event.message_edit: EventData(
        type_args=["Message", "Message"],
    ),
    Event.message_delete: EventData(
        type_args=["Message"],
    ),
    Event.bulk_message_delete: EventData(
        type_args=["List[Message]"],
    ),
    Event.raw_message_edit: EventData(
        type_args=["RawMessageUpdateEvent"],
    ),
    Event.raw_message_delete: EventData(
        type_args=["RawMessageDeleteEvent"],
    ),
    Event.raw_bulk_message_delete: EventData(
        type_args=["RawBulkMessageDeleteEvent"],
    ),
    Event.reaction_add: EventData(
        type_args=["Reaction", "Union[Member, User]"],
    ),
    Event.reaction_remove: EventData(
        type_args=["Reaction", "Union[Member, User]"],
    ),
    Event.reaction_clear: EventData(
        type_args=["Message", "List[Reaction]"],
    ),
    Event.reaction_clear_emoji: EventData(
        type_args=["Reaction"],
    ),
    Event.raw_reaction_add: EventData(
        type_args=["RawReactionActionEvent"],
    ),
    Event.raw_reaction_remove: EventData(
        type_args=["RawReactionActionEvent"],
    ),
    Event.raw_reaction_clear: EventData(
        type_args=["RawReactionClearEvent"],
    ),
    Event.raw_reaction_clear_emoji: EventData(
        type_args=["RawReactionClearEmojiEvent"],
    ),
    Event.typing: EventData(
        type_args=["Union[Messageable, ForumChannel]", "Union[User, Member]", "datetime"],
    ),
    Event.raw_typing: EventData(
        type_args=["RawTypingEvent"],
    ),
    Event.command: EventData(
        type_args=["commands.Context"],
        bot=True,
    ),
    Event.command_completion: EventData(
        type_args=["commands.Context"],
        bot=True,
    ),
    Event.command_error: EventData(
        type_args=["commands.Context", "commands.CommandError"],
        bot=True,
    ),
    Event.slash_command: EventData(
        type_args=["ApplicationCommandInteraction"],
        bot=True,
    ),
    Event.slash_command_completion: EventData(
        type_args=["ApplicationCommandInteraction"],
        bot=True,
    ),
    Event.slash_command_error: EventData(
        type_args=["ApplicationCommandInteraction", "commands.CommandError"],
        bot=True,
    ),
    Event.user_command: EventData(
        type_args=["ApplicationCommandInteraction"],
        bot=True,
    ),
    Event.user_command_completion: EventData(
        type_args=["ApplicationCommandInteraction"],
        bot=True,
    ),
    Event.user_command_error: EventData(
        type_args=["ApplicationCommandInteraction", "commands.CommandError"],
        bot=True,
    ),
    Event.message_command: EventData(
        type_args=["ApplicationCommandInteraction"],
        bot=True,
    ),
    Event.message_command_completion: EventData(
        type_args=["ApplicationCommandInteraction"],
        bot=True,
    ),
    Event.message_command_error: EventData(
        type_args=["ApplicationCommandInteraction", "commands.CommandError"],
        bot=True,
    ),
}
