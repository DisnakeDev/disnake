# SPDX-License-Identifier: MIT

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, List, Optional

from .enums import SubscriptionStatus, try_enum
from .mixins import Hashable
from .utils import parse_time, snowflake_time

if TYPE_CHECKING:
    from .state import ConnectionState
    from .types.subscription import Subscription as SubscriptionPayload
    from .user import User

__all__ = ("Subscription",)


class Subscription(Hashable):
    """Represents a subscription.

    This can only be retrieved using :meth:`SKU.subscriptions` or :meth:`SKU.fetch_subscription`,
    or provided by events (e.g. :func:`on_subscription_create`).

    .. warning::
        :class:`Subscription`\\s should not be used to grant perks. Use :class:`Entitlement`\\s as a way of determining whether a user should have access to a specific :class:`SKU`.

    .. note::
        Some subscriptions may have been canceled already; consider using :meth:`is_canceled` to check whether a given subscription was canceled.

    .. collapse:: operations

        .. describe:: x == y

            Checks if two :class:`Subscription`\\s are equal.

        .. describe:: x != y

            Checks if two :class:`Subscription`\\s are not equal.

        .. describe:: hash(x)

            Returns the subscription's hash.

    .. versionadded:: 2.10

    Attributes
    ----------
    id: :class:`int`
        The subscription's ID.
    user_id: :class:`int`
        The ID of the user who is subscribed to the :attr:`sku_ids`.

        See also :attr:`user`.
    sku_ids: List[:class:`int`]
        The ID of the SKUs the user is subscribed to.
    renewal_sku_ids: List[:class:`int`]
        The IDs of the SKUs that will be renewed at the start of the new period.
    entitlement_ids: List[:class:`int`]
        The IDs of the entitlements the user has as part of this subscription.
    current_period_start: :class:`datetime.datetime`
        The time at which the current period for the given subscription started.
    current_period_end: :class:`datetime.datetime`
        The time at which the current period for the given subscription will end.
    status: :class:`SubscriptionStatus`
        The current status of the given subscription.
    canceled_at: Optional[:class:`datetime.datetime`]
        The time at which the subscription was canceled.

        See also :attr:`is_canceled`.
    """

    __slots__ = (
        "_state",
        "id",
        "user_id",
        "sku_ids",
        "entitlement_ids",
        "renewal_sku_ids",
        "current_period_start",
        "current_period_end",
        "status",
        "canceled_at",
    )

    def __init__(self, *, data: SubscriptionPayload, state: ConnectionState) -> None:
        self._state: ConnectionState = state

        self.id: int = int(data["id"])
        self.user_id: int = int(data["user_id"])
        self.sku_ids: List[int] = list(map(int, data["sku_ids"]))
        self.entitlement_ids: List[int] = list(map(int, data["entitlement_ids"]))
        self.renewal_sku_ids: Optional[List[int]] = (
            list(map(int, renewal_sku_ids))
            if (renewal_sku_ids := data.get("renewal_sku_ids")) is not None
            else None
        )
        self.current_period_start: datetime.datetime = parse_time(data["current_period_start"])
        self.current_period_end: datetime.datetime = parse_time(data["current_period_end"])
        self.status: SubscriptionStatus = try_enum(SubscriptionStatus, data["status"])
        self.canceled_at: Optional[datetime.datetime] = parse_time(data["canceled_at"])

    @property
    def created_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: Returns the subscription's creation time in UTC."""
        return snowflake_time(self.id)

    @property
    def user(self) -> Optional[User]:
        """Optional[:class:`User`]: The user who is subscribed to the :attr:`sku_ids`.

        Requires the user to be cached.
        See also :attr:`user_id`.
        """
        return self._state.get_user(self.user_id)

    @property
    def is_canceled(self) -> bool:
        """:class:`bool`: Whether the subscription was canceled,
        based on :attr:`canceled_at`.
        """
        return self.canceled_at is not None
