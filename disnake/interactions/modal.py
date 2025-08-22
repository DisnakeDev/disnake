# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Generator, List, Optional

from ..enums import ComponentType
from ..message import Message
from ..utils import cached_slot_property
from .base import ClientT, Interaction

if TYPE_CHECKING:
    from ..state import ConnectionState
    from ..types.interactions import (
        ModalInteraction as ModalInteractionPayload,
        ModalInteractionActionRow as ModalInteractionActionRowPayload,
        ModalInteractionComponentData as ModalInteractionComponentDataPayload,
        ModalInteractionData as ModalInteractionDataPayload,
    )

__all__ = ("ModalInteraction", "ModalInteractionData")


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
    guild_id: Optional[:class:`int`]
        The guild ID the interaction was sent from.
    channel: Union[:class:`abc.GuildChannel`, :class:`Thread`, :class:`abc.PrivateChannel`, :class:`PartialMessageable`]
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

    author: Union[:class:`User`, :class:`Member`]
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

    guild_locale: Optional[:class:`Locale`]
        The selected language of the interaction's guild.
        This value is only meaningful in guilds with ``COMMUNITY`` feature and receives a default value otherwise.
        If the interaction was in a DM, then this value is ``None``.

        .. versionchanged:: 2.5
            Changed to :class:`Locale` instead of :class:`str`.

    client: :class:`Client`
        The interaction client.
    entitlements: List[:class:`Entitlement`]
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

    data: :class:`ModalInteractionData`
        The wrapped interaction data.
    message: Optional[:class:`Message`]
        The message that this interaction's modal originated from,
        if the modal was sent in response to a component interaction.

        .. versionadded:: 2.5
    """

    __slots__ = ("message", "_cs_text_values")

    def __init__(self, *, data: ModalInteractionPayload, state: ConnectionState) -> None:
        super().__init__(data=data, state=state)
        self.data: ModalInteractionData = ModalInteractionData(data=data["data"])

        if message_data := data.get("message"):
            message = Message(state=self._state, channel=self.channel, data=message_data)
        else:
            message = None
        self.message: Optional[Message] = message

    def walk_raw_components(self) -> Generator[ModalInteractionComponentDataPayload, None, None]:
        """Returns a generator that yields raw component data from action rows one by one, as provided by Discord.
        This does not contain all fields of the components due to API limitations.

        .. versionadded:: 2.6

        Returns
        -------
        Generator[:class:`dict`, None, None]
        """
        for action_row in self.data.components:
            yield from action_row["components"]

    @cached_slot_property("_cs_text_values")
    def text_values(self) -> Dict[str, str]:
        """Dict[:class:`str`, :class:`str`]: Returns the text values the user has entered in the modal.
        This is a dict of the form ``{custom_id: value}``.
        """
        text_input_type = ComponentType.text_input.value
        return {
            component["custom_id"]: component.get("value") or ""
            for component in self.walk_raw_components()
            if component.get("type") == text_input_type
        }

    @property
    def custom_id(self) -> str:
        """:class:`str`: The custom ID of the modal."""
        return self.data.custom_id


class ModalInteractionData(Dict[str, Any]):
    """Represents the data of an interaction with a modal.

    .. versionadded:: 2.4

    Attributes
    ----------
    custom_id: :class:`str`
        The custom ID of the modal.
    components: List[:class:`dict`]
        The raw component data of the modal interaction, as provided by Discord.
        This does not contain all fields of the components due to API limitations.

        .. versionadded:: 2.6
    """

    __slots__ = ("custom_id", "components")

    def __init__(self, *, data: ModalInteractionDataPayload) -> None:
        super().__init__(data)
        self.custom_id: str = data["custom_id"]
        # This uses a stripped-down action row TypedDict, as we only receive
        # partial data from the API, generally only containing `type`, `custom_id`,
        # and relevant fields like a select's `values`.
        self.components: List[ModalInteractionActionRowPayload] = data["components"]

    def __repr__(self) -> str:
        return f"<ModalInteractionData custom_id={self.custom_id!r} components={self.components!r}>"
