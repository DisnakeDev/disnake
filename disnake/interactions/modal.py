# SPDX-License-Identifier: MIT

from __future__ import annotations

from collections.abc import Generator, Sequence
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Optional,
    TypeVar,
    Union,
)

from disnake.components import _SELECT_COMPONENT_TYPE_VALUES
from disnake.enums import ComponentType
from disnake.interactions.base import ClientT, Interaction, InteractionDataResolved
from disnake.message import Attachment, Message
from disnake.utils import cached_slot_property

if TYPE_CHECKING:
    from disnake.abc import AnyChannel
    from disnake.member import Member
    from disnake.role import Role
    from disnake.state import ConnectionState
    from disnake.types.interactions import (
        ModalInteraction as ModalInteractionPayload,
        ModalInteractionComponentData as ModalInteractionComponentDataPayload,
        ModalInteractionData as ModalInteractionDataPayload,
        ModalInteractionInnerComponentData as ModalInteractionInnerComponentDataPayload,
    )
    from disnake.types.snowflake import Snowflake
    from disnake.user import User

__all__ = ("ModalInteraction", "ModalInteractionData")


T = TypeVar("T")

# {custom_id: text_input_value | select_values | attachments}
ResolvedValues = dict[str, Union[str, Sequence[T]]]


class ModalInteraction(Interaction[ClientT]):
    """Represents an interaction with a modal.

    .. versionadded:: 2.4

    Attributes
    ----------
    id: :class:`int`
        The interaction's ID.
    type: :class:`InteractionType`
        The interaction type.
    application_id: :class:`int`
        The application ID that the interaction was for.
    token: :class:`str`
        The token to continue the interaction.
        These are valid for 15 minutes.
    guild_id: :class:`int` | :data:`None`
        The guild ID the interaction was sent from.
    channel: :class:`abc.GuildChannel` | :class:`Thread` | :class:`abc.PrivateChannel` | :class:`PartialMessageable`
        The channel the interaction was sent from.

        Note that due to a Discord limitation, DM channels
        may not contain recipient information.
        Unknown channel types will be :class:`PartialMessageable`.

        .. versionchanged:: 2.10
            If the interaction was sent from a thread and the bot cannot normally access the thread,
            this is now a proper :class:`Thread` object.
            Private channels are now proper :class:`DMChannel`/:class:`GroupChannel`
            objects instead of :class:`PartialMessageable`.

        .. note::
            If you want to compute the interaction author's or bot's permissions in the channel,
            consider using :attr:`permissions` or :attr:`app_permissions`.

    author: :class:`User` | :class:`Member`
        The user or member that sent the interaction.

        .. note::
            In scenarios where an interaction occurs in a guild but :attr:`.guild` is unavailable,
            such as with user-installed applications in guilds, some attributes of :class:`Member`\\s
            that depend on the guild/role cache will not work due to an API limitation.
            This includes :attr:`~Member.roles`, :attr:`~Member.top_role`, :attr:`~Member.role_icon`,
            and :attr:`~Member.guild_permissions`.
    locale: :class:`Locale`
        The selected language of the interaction's author.

        .. versionchanged:: 2.5
            Changed to :class:`Locale` instead of :class:`str`.

    guild_locale: :class:`Locale` | :data:`None`
        The selected language of the interaction's guild.
        This value is only meaningful in guilds with ``COMMUNITY`` feature and receives a default value otherwise.
        If the interaction was in a DM, then this value is :data:`None`.

        .. versionchanged:: 2.5
            Changed to :class:`Locale` instead of :class:`str`.

    client: :class:`Client`
        The interaction client.
    entitlements: :class:`list`\\[:class:`Entitlement`]
        The entitlements for the invoking user and guild,
        representing access to an application subscription.

        .. versionadded:: 2.10

    authorizing_integration_owners: :class:`AuthorizingIntegrationOwners`
        Details about the authorizing user/guild for the application installation
        related to the interaction.

        .. versionadded:: 2.10

    context: :class:`InteractionContextTypes`
        The context where the interaction was triggered from.

        This is a flag object, with exactly one of the flags set to ``True``.
        To check whether an interaction originated from e.g. a :attr:`~InteractionContextTypes.guild`
        context, you can use ``if interaction.context.guild:``.

        .. versionadded:: 2.10

    attachment_size_limit: :class:`int`
        The maximum number of bytes files can have in responses to this interaction.

        This may be higher than the default limit, depending on the guild's boost
        status or the invoking user's nitro status.

        .. versionadded:: 2.11

    data: :class:`ModalInteractionData`
        The wrapped interaction data.
    message: :class:`Message` | :data:`None`
        The message that this interaction's modal originated from,
        if the modal was sent in response to a component interaction.

        .. versionadded:: 2.5
    """

    __slots__ = ("message", "_cs_values", "_cs_resolved_values", "_cs_text_values")

    def __init__(self, *, data: ModalInteractionPayload, state: ConnectionState) -> None:
        super().__init__(data=data, state=state)
        self.data: ModalInteractionData = ModalInteractionData(data=data["data"], parent=self)

        if message_data := data.get("message"):
            message = Message(state=self._state, channel=self.channel, data=message_data)
        else:
            message = None
        self.message: Optional[Message] = message

    def _walk_components(
        self,
        components: Sequence[
            Union[ModalInteractionComponentDataPayload, ModalInteractionInnerComponentDataPayload]
        ],
    ) -> Generator[ModalInteractionInnerComponentDataPayload, None, None]:
        for component in components:
            if component["type"] == ComponentType.action_row.value:
                yield from self._walk_components(component["components"])
            elif component["type"] == ComponentType.label.value:
                yield from self._walk_components([component["component"]])
            elif component["type"] == ComponentType.text_display.value:
                continue
            else:
                yield component

    def walk_raw_components(
        self,
    ) -> Generator[ModalInteractionInnerComponentDataPayload, None, None]:
        """Returns a generator that yields raw component data of the innermost/non-layout
        components one by one, as provided by Discord.
        This does not contain all fields of the components due to API limitations.

        .. versionadded:: 2.6

        Returns
        -------
        :class:`~collections.abc.Generator`\\[:class:`dict`, None, None]
        """
        yield from self._walk_components(self.data.components)

    def _resolve_values(
        self, resolve: Callable[[Snowflake, ComponentType], T]
    ) -> ResolvedValues[Union[str, T]]:
        values: ResolvedValues[Union[str, T]] = {}
        for component in self.walk_raw_components():
            if component["type"] == ComponentType.text_input.value:
                value = component.get("value")
            elif component["type"] == ComponentType.string_select.value:
                value = component.get("values")
            elif (
                component["type"] in _SELECT_COMPONENT_TYPE_VALUES
                or component["type"] == ComponentType.file_upload.value
            ):
                # auto-populated selects
                component_type = ComponentType(component["type"])
                value = [resolve(v, component_type) for v in component.get("values") or []]
            else:
                continue
            values[component["custom_id"]] = value
        return values

    @cached_slot_property("_cs_values")
    def values(self) -> ResolvedValues[str]:
        """:class:`dict`\\[:class:`str`, :class:`str` | :class:`~collections.abc.Sequence`\\[:class:`str`]]: Returns all raw values the user has entered in the modal.
        This is a dict of the form ``{custom_id: value}``.

        For select menus, the corresponding dict value is a list of the values the user has selected.
        For select menus of type :attr:`~ComponentType.string_select`,
        these are just the string values the user selected;
        for other select menu types, these are the IDs of the selected entities.

        See also :attr:`resolved_values`.

        .. versionadded:: 2.11
        """
        return self._resolve_values(lambda id, type: str(id))

    @cached_slot_property("_cs_resolved_values")
    def resolved_values(
        self,
    ) -> ResolvedValues[Union[str, Member, User, Role, AnyChannel, Attachment]]:
        """:class:`dict`\\[:class:`str`, :class:`str` | :class:`~collections.abc.Sequence`\\[:class:`str` | :class:`Member` | :class:`User` | :class:`Role` | :class:`abc.GuildChannel` | :class:`Thread` | :class:`PartialMessageable` | :class:`Attachment`]]: The (resolved) values the user entered in the modal.
        This is a dict of the form ``{custom_id: value}``.

        For select menus, the corresponding dict value is a list of the values the user has selected.
        For select menus of type :attr:`~ComponentType.string_select`,
        this is equivalent to :attr:`values`;
        for other select menu types, these are full objects corresponding to the selected entities.

        For file uploads, the corresponding dict value is a list of files the user has uploaded.

        .. versionadded:: 2.11
        """
        resolved_data = self.data.resolved
        # we expect the api to only provide valid values; there won't be any messages/attachments here.
        return self._resolve_values(lambda id, type: resolved_data.get_with_type(id, type, str(id)))  # pyright: ignore[reportReturnType]

    @cached_slot_property("_cs_text_values")
    def text_values(self) -> dict[str, str]:
        """:class:`dict`\\[:class:`str`, :class:`str`]: Returns the text values the user has entered in the modal.
        This is a dict of the form ``{custom_id: value}``.
        """
        text_input_type = ComponentType.text_input.value
        return {
            component["custom_id"]: component.get("value") or ""
            for component in self.walk_raw_components()
            if component["type"] == text_input_type
        }

    @property
    def custom_id(self) -> str:
        """:class:`str`: The custom ID of the modal."""
        return self.data.custom_id


class ModalInteractionData(dict[str, Any]):
    """Represents the data of an interaction with a modal.

    .. versionadded:: 2.4

    Attributes
    ----------
    custom_id: :class:`str`
        The custom ID of the modal.
    components: :class:`list`\\[:class:`dict`]
        The raw component data of the modal interaction, as provided by Discord.
        This does not contain all fields of the components due to API limitations.

        .. versionadded:: 2.6
    resolved: :class:`InteractionDataResolved`
        All resolved objects related to this interaction.

        .. versionadded:: 2.11
    """

    __slots__ = ("custom_id", "components", "resolved")

    def __init__(
        self,
        *,
        data: ModalInteractionDataPayload,
        parent: ModalInteraction[ClientT],
    ) -> None:
        super().__init__(data)
        self.custom_id: str = data["custom_id"]
        # This uses stripped-down component dicts, as we only receive
        # partial data from the API, generally only containing `type`, `custom_id`, `id`,
        # and relevant fields like a select's `values`.
        self.components: list[ModalInteractionComponentDataPayload] = data["components"]
        self.resolved: InteractionDataResolved = InteractionDataResolved(
            data=data.get("resolved", {}), parent=parent
        )

    def __repr__(self) -> str:
        return f"<ModalInteractionData custom_id={self.custom_id!r} components={self.components!r}>"
