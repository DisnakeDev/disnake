# SPDX-License-Identifier: MIT

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Optional

from .enums import EntitlementType, try_enum
from .mixins import Hashable
from .utils import _get_as_snowflake, parse_time, snowflake_time, utcnow

if TYPE_CHECKING:
    from .guild import Guild
    from .state import ConnectionState
    from .types.entitlement import Entitlement as EntitlementPayload
    from .user import User


__all__ = ("Entitlement",)


class Entitlement(Hashable):
    """Represents an entitlement.

    This is usually retrieved using :meth:`Client.entitlements`, from
    :attr:`Interaction.entitlements` when using interactions, or provided by
    events (e.g. :func:`on_entitlement_create`).

    Note that some entitlements may have ended already; consider using
    :meth:`is_active` to check whether a given entitlement is considered active at the current time,
    or use ``exclude_ended=True`` when fetching entitlements using :meth:`Client.entitlements`.

    You may create new entitlements for testing purposes using :meth:`Client.create_entitlement`.

    .. collapse:: operations

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

        See also :attr:`user`.
    guild_id: Optional[:class:`int`]
        The ID of the guild that is granted access to the entitlement's SKU.

        See also :attr:`guild`.
    application_id: :class:`int`
        The parent application's ID.
    deleted: :class:`bool`
        Whether the entitlement has been deleted.
    consumed: :class:`bool`
        Whether the entitlement has been consumed. Only applies to consumable items,
        i.e. those associated with a :attr:`~SKUType.consumable` SKU.
    starts_at: Optional[:class:`datetime.datetime`]
        The time at which the entitlement starts being active.
        Set to ``None`` when this is a test entitlement.
    ends_at: Optional[:class:`datetime.datetime`]
        The time at which the entitlement stops being active.

        You can use :meth:`is_active` to check whether this entitlement is still active.
    """

    __slots__ = (
        "_state",
        "id",
        "sku_id",
        "user_id",
        "guild_id",
        "application_id",
        "type",
        "deleted",
        "consumed",
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
        self.deleted: bool = data.get("deleted", False)
        self.consumed: bool = data.get("consumed", False)
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
    def created_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: Returns the entitlement's creation time in UTC."""
        return snowflake_time(self.id)

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

        Requires the user to be cached.
        See also :attr:`user_id`.
        """
        return self._state.get_user(self.user_id)

    def is_active(self) -> bool:
        """Whether the entitlement is currently active,
        based on :attr:`starts_at` and :attr:`ends_at`.

        Always returns ``True`` for test entitlements.

        :return type: :class:`bool`
        """
        if self.deleted:
            return False

        now = utcnow()
        if self.starts_at is not None and now < self.starts_at:
            return False
        if self.ends_at is not None and now >= self.ends_at:
            return False

        return True

    async def consume(self) -> None:
        """|coro|

        Marks the entitlement as consumed.

        This is only valid for consumable one-time entitlements; see :attr:`consumed`.

        Raises
        ------
        NotFound
            The entitlement does not exist.
        HTTPException
            Consuming the entitlement failed.
        """
        await self._state.http.consume_entitlement(self.application_id, self.id)

    async def delete(self) -> None:
        """|coro|

        Deletes the entitlement.

        This is only valid for test entitlements; you cannot use this to
        delete entitlements that users purchased.

        Raises
        ------
        NotFound
            The entitlement does not exist.
        HTTPException
            Deleting the entitlement failed.
        """
        await self._state.http.delete_test_entitlement(self.application_id, self.id)
