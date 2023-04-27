# SPDX-License-Identifier: MIT

import types
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, cast

import libcst as cst
import libcst.matchers as m
from libcst import codemod

from disnake import Event


def get_param(func: cst.FunctionDef, name: str) -> cst.Param:
    results = m.findall(func.params, m.Param(m.Name(name)))
    assert len(results) == 1
    return cast(cst.Param, results[0])


class EventTypings(codemod.VisitorBasedCodemodCommand):
    DESCRIPTION: str = "Adds overloads for library events."

    flag_classes: List[str]
    imported_module: types.ModuleType

    def transform_module(self, tree: cst.Module) -> cst.Module:
        if "@_overload_with_events" not in tree.code:
            raise codemod.SkipFile(
                "this module does not contain the required decorator: `@_overload_with_events`."
            )
        return super().transform_module(tree)

    def visit_FunctionDef(self, node: cst.FunctionDef) -> Optional[bool]:
        # don't recurse into the body of a function
        return False

    def leave_FunctionDef(self, _: cst.FunctionDef, node: cst.FunctionDef):
        decorators = [
            deco.decorator.value
            for deco in node.decorators
            if not isinstance(deco.decorator, cst.Call)
        ]
        if "_generated" in decorators:
            # remove generated methods
            return cst.RemovalSentinel.REMOVE
        if "_overload_with_events" not in decorators:
            # ignore
            return node

        if node.name.value != "wait_for":
            raise RuntimeError(
                f"unknown method '{node.name.value}' with @_overload_with_events decorator"
            )

        # if we're here, we found a @_overload_with_events decorator
        new_overloads: List[cst.FunctionDef] = []
        for event in Event:
            event_data = EVENT_DATA[event]
            if event_data.event_only:
                continue
            args = event_data.args

            new_overload = node.with_changes(
                body=cst.IndentedBlock([cst.SimpleStatementLine([cst.Expr(cst.Ellipsis())])]),
                decorators=[
                    cst.Decorator(cst.Name("overload")),
                    cst.Decorator(cst.Name("_generated")),
                ],
                leading_lines=(),
            )

            # set `event` annotation
            new_annotation = cst.parse_expression(
                # the lazy way of doing things
                f'Literal[Event.{event.name}, "{event.value}"]',
                config=self.module.config_for_parsing,
            )
            new_overload = new_overload.with_deep_changes(
                get_param(new_overload, "event"), annotation=cst.Annotation(new_annotation)
            )

            # set `check` annotation
            callable_annotation = m.findall(
                get_param(new_overload, "check"), m.Subscript(m.Name("Callable"))
            )[0]
            callable_params = m.findall(callable_annotation, m.Ellipsis())[0]
            new_annotation = cst.parse_expression(
                f'[{",".join(args)}]',
                config=self.module.config_for_parsing,
            )
            new_overload = new_overload.deep_replace(callable_params, new_annotation)

            # set return annotation
            if len(args) == 0:
                new_annotation_str = "None"
            elif len(args) == 1:
                new_annotation_str = args[0]
            else:
                new_annotation_str = f'Tuple[{",".join(args)}]'
            new_annotation = cst.parse_expression(
                f"Coroutine[Any, Any, {new_annotation_str}]", config=self.module.config_for_parsing
            )
            new_overload = new_overload.with_changes(returns=cst.Annotation(new_annotation))

            # set `self` annotation as a workaround for overloads in subclasses
            if event_data.bot:
                new_overload = new_overload.with_deep_changes(
                    get_param(new_overload, "self"),
                    annotation=cst.Annotation(cst.Name("AnyBot")),
                )

            new_overloads.append(new_overload)

        return cst.FlattenSentinel([*new_overloads, node])


@dataclass
class EventData:
    # type names of event arguments, e.g. `("Guild", "User")`
    args: Tuple[str, ...]
    # whether the event is specific to ext.commands
    bot: bool = False
    # whether the event can only be used through `@event` and not other listeners
    event_only: bool = False


EVENT_DATA: Dict[Event, EventData] = {
    Event.connect: EventData(()),
    Event.disconnect: EventData(()),
    # TODO: figure out how to specify varargs for these two
    Event.error: EventData((), event_only=True),
    Event.gateway_error: EventData((), event_only=True),
    Event.ready: EventData(()),
    Event.resumed: EventData(()),
    Event.shard_connect: EventData(("int",)),
    Event.shard_disconnect: EventData(("int",)),
    Event.shard_ready: EventData(("int",)),
    Event.shard_resumed: EventData(("int",)),
    Event.socket_event_type: EventData(("str",)),
    Event.socket_raw_receive: EventData(("str",)),
    Event.socket_raw_send: EventData(("Union[str, bytes]",)),
    Event.guild_channel_create: EventData(("GuildChannel",)),
    Event.guild_channel_update: EventData(("GuildChannel", "GuildChannel")),
    Event.guild_channel_delete: EventData(("GuildChannel",)),
    Event.guild_channel_pins_update: EventData(
        ("Union[GuildChannel, Thread]", "Optional[datetime]")
    ),
    Event.invite_create: EventData(("Invite",)),
    Event.invite_delete: EventData(("Invite",)),
    Event.private_channel_update: EventData(("GroupChannel", "GroupChannel")),
    Event.private_channel_pins_update: EventData(("PrivateChannel", "Optional[datetime]")),
    Event.webhooks_update: EventData(("GuildChannel",)),
    Event.thread_create: EventData(("Thread",)),
    Event.thread_update: EventData(("Thread", "Thread")),
    Event.thread_delete: EventData(("Thread",)),
    Event.thread_join: EventData(("Thread",)),
    Event.thread_remove: EventData(("Thread",)),
    Event.thread_member_join: EventData(("ThreadMember",)),
    Event.thread_member_remove: EventData(("ThreadMember",)),
    Event.raw_thread_member_remove: EventData(("RawThreadMemberRemoveEvent",)),
    Event.raw_thread_update: EventData(("Thread",)),
    Event.raw_thread_delete: EventData(("RawThreadDeleteEvent",)),
    Event.guild_join: EventData(("Guild",)),
    Event.guild_remove: EventData(("Guild",)),
    Event.guild_update: EventData(("Guild", "Guild")),
    Event.guild_available: EventData(("Guild",)),
    Event.guild_unavailable: EventData(("Guild",)),
    Event.guild_role_create: EventData(("Role",)),
    Event.guild_role_delete: EventData(("Role",)),
    Event.guild_role_update: EventData(("Role", "Role")),
    Event.guild_emojis_update: EventData(("Guild", "Sequence[Emoji]", "Sequence[Emoji]")),
    Event.guild_stickers_update: EventData(
        ("Guild", "Sequence[GuildSticker]", "Sequence[GuildSticker]")
    ),
    Event.guild_integrations_update: EventData(("Guild",)),
    Event.guild_scheduled_event_create: EventData(("GuildScheduledEvent",)),
    Event.guild_scheduled_event_update: EventData(("GuildScheduledEvent", "GuildScheduledEvent")),
    Event.guild_scheduled_event_delete: EventData(("GuildScheduledEvent",)),
    Event.guild_scheduled_event_subscribe: EventData(
        ("GuildScheduledEvent", "Union[Member, User]")
    ),
    Event.guild_scheduled_event_unsubscribe: EventData(
        ("GuildScheduledEvent", "Union[Member, User]")
    ),
    Event.raw_guild_scheduled_event_subscribe: EventData(
        ("RawGuildScheduledEventUserActionEvent",)
    ),
    Event.raw_guild_scheduled_event_unsubscribe: EventData(
        ("RawGuildScheduledEventUserActionEvent",)
    ),
    Event.application_command_permissions_update: EventData(
        ("GuildApplicationCommandPermissions",)
    ),
    Event.automod_action_execution: EventData(("AutoModActionExecution",)),
    Event.automod_rule_create: EventData(("AutoModRule",)),
    Event.automod_rule_update: EventData(("AutoModRule",)),
    Event.automod_rule_delete: EventData(("AutoModRule",)),
    Event.audit_log_entry_create: EventData(("AuditLogEntry",)),
    Event.integration_create: EventData(("Integration",)),
    Event.integration_update: EventData(("Integration",)),
    Event.raw_integration_delete: EventData(("RawIntegrationDeleteEvent",)),
    Event.member_join: EventData(("Member",)),
    Event.member_remove: EventData(("Member",)),
    Event.member_update: EventData(("Member", "Member")),
    Event.raw_member_remove: EventData(("RawGuildMemberRemoveEvent",)),
    Event.raw_member_update: EventData(("Member",)),
    Event.member_ban: EventData(("Guild", "Union[User, Member]")),
    Event.member_unban: EventData(("Guild", "User")),
    Event.presence_update: EventData(("Member", "Member")),
    Event.user_update: EventData(("User", "User")),
    Event.voice_state_update: EventData(("Member", "VoiceState", "VoiceState")),
    Event.stage_instance_create: EventData(("StageInstance",)),
    Event.stage_instance_delete: EventData(("StageInstance", "StageInstance")),
    Event.stage_instance_update: EventData(("StageInstance",)),
    Event.application_command: EventData(("ApplicationCommandInteraction",)),
    Event.application_command_autocomplete: EventData(("ApplicationCommandInteraction",)),
    Event.button_click: EventData(("MessageInteraction",)),
    Event.dropdown: EventData(("MessageInteraction",)),
    Event.interaction: EventData(("Interaction",)),
    Event.message_interaction: EventData(("MessageInteraction",)),
    Event.modal_submit: EventData(("ModalInteraction",)),
    Event.message: EventData(("Message",)),
    Event.message_edit: EventData(("Message", "Message")),
    Event.message_delete: EventData(("Message",)),
    Event.bulk_message_delete: EventData(("List[Message]",)),
    Event.raw_message_edit: EventData(("RawMessageUpdateEvent",)),
    Event.raw_message_delete: EventData(("RawMessageDeleteEvent",)),
    Event.raw_bulk_message_delete: EventData(("RawBulkMessageDeleteEvent",)),
    Event.reaction_add: EventData(("Reaction", "Union[Member, User]")),
    Event.reaction_remove: EventData(("Reaction", "Union[Member, User]")),
    Event.reaction_clear: EventData(("Message", "List[Reaction]")),
    Event.reaction_clear_emoji: EventData(("Reaction",)),
    Event.raw_reaction_add: EventData(("RawReactionActionEvent",)),
    Event.raw_reaction_remove: EventData(("RawReactionActionEvent",)),
    Event.raw_reaction_clear: EventData(("RawReactionClearEvent",)),
    Event.raw_reaction_clear_emoji: EventData(("RawReactionClearEmojiEvent",)),
    Event.typing: EventData(
        ("Union[Messageable, ForumChannel]", "Union[User, Member]", "datetime")
    ),
    Event.raw_typing: EventData(("RawTypingEvent",)),
    Event.command: EventData(("commands.Context",), bot=True),
    Event.command_completion: EventData(("commands.Context",), bot=True),
    Event.command_error: EventData(("commands.Context", "commands.CommandError"), bot=True),
    Event.slash_command: EventData(("ApplicationCommandInteraction",), bot=True),
    Event.slash_command_completion: EventData(("ApplicationCommandInteraction",), bot=True),
    Event.slash_command_error: EventData(
        ("ApplicationCommandInteraction", "commands.CommandError"), bot=True
    ),
    Event.user_command: EventData(("ApplicationCommandInteraction",), bot=True),
    Event.user_command_completion: EventData(("ApplicationCommandInteraction",), bot=True),
    Event.user_command_error: EventData(
        ("ApplicationCommandInteraction", "commands.CommandError"), bot=True
    ),
    Event.message_command: EventData(("ApplicationCommandInteraction",), bot=True),
    Event.message_command_completion: EventData(("ApplicationCommandInteraction",), bot=True),
    Event.message_command_error: EventData(
        ("ApplicationCommandInteraction", "commands.CommandError"), bot=True
    ),
}
