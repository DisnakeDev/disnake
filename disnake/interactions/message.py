# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Union

from ..components import MessageComponent
from ..enums import ComponentType, try_enum
from ..message import Message
from ..utils import cached_slot_property
from .base import Interaction, InteractionDataResolved

__all__ = (
    "MessageInteraction",
    "MessageInteractionData",
)

if TYPE_CHECKING:
    from ..member import Member
    from ..role import Role
    from ..state import ConnectionState
    from ..types.interactions import (
        InteractionDataResolved as InteractionDataResolvedPayload,
        MessageComponentInteractionData as MessageComponentInteractionDataPayload,
        MessageInteraction as MessageInteractionPayload,
    )
    from ..user import User
    from .base import InteractionChannel


class MessageInteraction(Interaction):
    """Represents an interaction with a message component.

    Current examples are buttons and dropdowns.

    .. versionadded:: 2.1

    Attributes
    ----------
    id: :class:`int`
        The interaction's ID.
    type: :class:`InteractionType`
        The interaction type.
    application_id: :class:`int`
        The application ID that the interaction was for.
    token: :class:`str`
        The token to continue the interaction. These are valid for 15 minutes.
    guild_id: Optional[:class:`int`]
        The guild ID the interaction was sent from.
    channel_id: :class:`int`
        The channel ID the interaction was sent from.
    author: Union[:class:`User`, :class:`Member`]
        The user or member that sent the interaction.
    locale: :class:`Locale`
        The selected language of the interaction's author.

        .. versionadded:: 2.4

        .. versionchanged:: 2.5
            Changed to :class:`Locale` instead of :class:`str`.

    guild_locale: Optional[:class:`Locale`]
        The selected language of the interaction's guild.
        This value is only meaningful in guilds with ``COMMUNITY`` feature and receives a default value otherwise.
        If the interaction was in a DM, then this value is ``None``.

        .. versionadded:: 2.4

        .. versionchanged:: 2.5
            Changed to :class:`Locale` instead of :class:`str`.

    message: Optional[:class:`Message`]
        The message that sent this interaction.
    data: :class:`MessageInteractionData`
        The wrapped interaction data.
    client: :class:`Client`
        The interaction client.
    """

    def __init__(self, *, data: MessageInteractionPayload, state: ConnectionState) -> None:
        super().__init__(data=data, state=state)
        self.data: MessageInteractionData = MessageInteractionData(
            data=data["data"], state=state, guild_id=self.guild_id
        )
        self.message = Message(state=self._state, channel=self.channel, data=data["message"])

    @property
    def values(self) -> Optional[List[str]]:
        """Optional[List[:class:`str`]]: The values the user selected.

        For select menus of type :attr:`~ComponentType.string_select`,
        these are just the string values the user selected.
        For other select menu types, these are the IDs of the selected entities.

        See also :attr:`resolved_values`.
        """
        return self.data.values

    @cached_slot_property("_cs_resolved_values")
    def resolved_values(
        self,
    ) -> Optional[Sequence[Union[str, Member, User, Role, InteractionChannel]]]:
        """Optional[Sequence[:class:`str`, :class:`Member`, :class:`User`, :class:`Role`, Union[:class:`abc.GuildChannel`, :class:`Thread`, :class:`PartialMessageable`]]]: The (resolved) values the user selected.

        For select menus of type :attr:`~ComponentType.string_select`,
        this is equivalent to :attr:`values`.
        For other select menu types, these are full objects corresponding to the selected entities.

        .. versionadded:: 2.7
        """
        if self.data.values is None:
            return None

        component_type = self.data.component_type
        # return values as-is if it's a string select
        if component_type is ComponentType.string_select:
            return self.data.values

        resolved = self.data.resolved
        values: List[Union[Member, User, Role, InteractionChannel]] = []
        for key in self.data.values:
            # force upcast to avoid typing issues; we expect the api to only provide valid values
            value: Any = resolved.get_with_type(key, component_type, key)
            values.append(value)
        return values

    @cached_slot_property("_cs_component")
    def component(self) -> MessageComponent:
        """Union[:class:`Button`, :class:`BaseSelectMenu`]: The component the user interacted with"""
        for action_row in self.message.components:
            for component in action_row.children:
                if component.custom_id == self.data.custom_id:
                    return component

        raise Exception("MessageInteraction is malformed - no component found")


class MessageInteractionData(Dict[str, Any]):
    """Represents the data of an interaction with a message component.

    .. versionadded:: 2.1

    Attributes
    ----------
    custom_id: :class:`str`
        The custom ID of the component.
    component_type: :class:`ComponentType`
        The type of the component.
    values: Optional[List[:class:`str`]]
        The values the user has selected in a select menu.
        For non-string select menus, this contains IDs for use with :attr:`resolved`.
    resolved: :class:`InteractionDataResolved`
        All resolved objects related to this interaction.

        .. versionadded:: 2.7
    """

    __slots__ = ("custom_id", "component_type", "values", "resolved")

    def __init__(
        self,
        *,
        data: MessageComponentInteractionDataPayload,
        state: ConnectionState,
        guild_id: Optional[int],
    ) -> None:
        super().__init__(data)
        self.custom_id: str = data["custom_id"]
        self.component_type: ComponentType = try_enum(ComponentType, data["component_type"])
        self.values: Optional[List[str]] = (
            list(map(str, values)) if (values := data.get("values")) else None
        )

        empty_resolved: InteractionDataResolvedPayload = {}  # pyright shenanigans
        self.resolved = InteractionDataResolved(
            data=data.get("resolved", empty_resolved), state=state, guild_id=guild_id
        )

    def __repr__(self) -> str:
        return (
            f"<MessageInteractionData custom_id={self.custom_id!r} "
            f"component_type={self.component_type!r} values={self.values!r}>"
        )
