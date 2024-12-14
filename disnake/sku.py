# SPDX-License-Identifier: MIT

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from .enums import SKUType, try_enum
from .flags import SKUFlags
from .mixins import Hashable
from .subscription import Subscription
from .utils import snowflake_time

if TYPE_CHECKING:
    from .state import ConnectionState
    from .types.sku import SKU as SKUPayload


__all__ = ("SKU",)


class SKU(Hashable):
    """Represents an SKU.

    This can be retrieved using :meth:`Client.skus`.

    .. collapse:: operations

        .. describe:: x == y

            Checks if two :class:`SKU`\\s are equal.

        .. describe:: x != y

            Checks if two :class:`SKU`\\s are not equal.

        .. describe:: hash(x)

            Returns the SKU's hash.

        .. describe:: str(x)

            Returns the SKU's name.

    .. versionadded:: 2.10

    Attributes
    ----------
    id: :class:`int`
        The SKU's ID.
    type: :class:`SKUType`
        The SKU's type.
    application_id: :class:`int`
        The parent application's ID.
    name: :class:`str`
        The SKU's name.
    slug: :class:`str`
        The SKU's URL slug, system-generated based on :attr:`name`.
    """

    __slots__ = ("_state", "id", "type", "application_id", "name", "slug", "_flags")

    def __init__(self, *, data: SKUPayload, state: ConnectionState) -> None:
        self._state: ConnectionState = state
        self.id: int = int(data["id"])
        self.type: SKUType = try_enum(SKUType, data["type"])
        self.application_id: int = int(data["application_id"])
        self.name: str = data["name"]
        self.slug: str = data["slug"]
        self._flags: int = data.get("flags", 0)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<SKU id={self.id!r} type={self.type!r} name={self.name!r}>"

    @property
    def created_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: Returns the SKU's creation time in UTC."""
        return snowflake_time(self.id)

    @property
    def flags(self) -> SKUFlags:
        """:class:`SKUFlags`: Returns the SKU's flags."""
        return SKUFlags._from_value(self._flags)

    async def subscriptions(self):
        """|coro|

        Retrieve all the subscriptions for this SKU.
        """
        ...

    async def fetch_subscription(self, subscription_id: int, /) -> Subscription:
        """|coro|

        Retrieve a subscription for this SKU given its ID.

        Raises
        ------
        NotFound
            The subscription does not exist.
        HTTPException
            Retrieving the subscription failed.
        """
        data = await self._state.http.get_subscription(self.id, subscription_id)
        return Subscription(data=data, state=self._state)
