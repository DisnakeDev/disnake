# SPDX-License-Identifier: MIT

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Optional

from .enums import EntitlementType, try_enum
from .mixins import Hashable
from .utils import _get_as_snowflake, parse_time, utcnow

if TYPE_CHECKING:
    from .guild import Guild
    from .state import ConnectionState
    from .types.entitlement import Entitlement as EntitlementPayload
    from .user import User


__all__ = ("Entitlement",)


class Entitlement(Hashable):
    """Represents an entitlement.

    This can be retrieved using :meth:`Client.entitlements`, from
    :attr:`Interaction.entitlements` when using interactions, or from the
    :func:`on_entitlement_create`/:func:`on_entitlement_update` events.

    .. container:: operations

        .. describe:: x == y

            Checks if two :class:`Entitlement`\\s are equal.

        .. describe:: x != y

            Checks if two :class:`Entitlement`\\s are not equal.

        .. describe:: hash(x)

            Returns the entitlement's hash.

    .. versionadded:: 2.10

    Attributes
    ----------
    id: :class:`int`
        The entitlement's ID.
    type: :class:`EntitlementType`
        The entitlement's type.
    sku_id: :class:`int`
        The ID of the associated SKU.
    user_id: Optional[:class:`int`]
        The ID of the user that is granted access to the entitlement's SKU.
    guild_id: Optional[:class:`int`]
        The ID of the guild that is granted access to the entitlement's SKU.
    application_id: :class:`int`
        The parent application's ID.
    starts_at: Optional[:class:`datetime.datetime`]
        The time at which the entitlement starts being valid.
        Set to ``None`` when this is a test entitlement.
    ends_at: Optional[:class:`datetime.datetime`]
        The time at which the entitlement stops being valid.
        Set to ``None`` when this is a test entitlement.
    """

    __slots__ = (
        "_state",
        "id",
        "sku_id",
        "user_id",
        "guild_id",
        "application_id",
        "type",
        "starts_at",
        "ends_at",
    )

    def __init__(self, *, data: EntitlementPayload, state: ConnectionState) -> None:
        self._state: ConnectionState = state

        self.id: int = int(data["id"])
        self.sku_id: int = int(data["sku_id"])
        self.user_id: Optional[int] = _get_as_snowflake(data, "user_id")
        self.guild_id: Optional[int] = _get_as_snowflake(data, "guild_id")
        self.application_id: int = int(data["application_id"])
        self.type: EntitlementType = try_enum(EntitlementType, data["type"])
        self.starts_at: Optional[datetime.datetime] = parse_time(data.get("starts_at"))
        self.ends_at: Optional[datetime.datetime] = parse_time(data.get("ends_at"))

    def __repr__(self) -> str:
        # presumably one of these is set
        if self.user_id:
            grant_repr = f"user_id={self.user_id!r}"
        else:
            grant_repr = f"guild_id={self.guild_id!r}"
        return (
            f"<Entitlement id={self.id!r} sku_id={self.sku_id!r} type={self.type!r} {grant_repr}>"
        )

    @property
    def guild(self) -> Optional[Guild]:
        """Optional[:class:`Guild`]: The guild that is granted access to
        this entitlement's SKU, if applicable.
        """
        return self._state._get_guild(self.guild_id)

    @property
    def user(self) -> Optional[User]:
        """Optional[:class:`User`]: The user that is granted access to
        this entitlement's SKU, if applicable.
        """
        return self._state.get_user(self.user_id)

    # TODO: naming - (is_)valid/active/expired ?
    @property
    def is_valid(self) -> bool:
        now = utcnow()
        if self.starts_at is not None and now < self.starts_at:
            return False
        if self.ends_at is not None and now >= self.ends_at:
            return False
        return True
