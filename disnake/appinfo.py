# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from . import utils
from .asset import Asset
from .flags import ApplicationFlags
from .permissions import Permissions

if TYPE_CHECKING:
    from .guild import Guild
    from .state import ConnectionState
    from .types.appinfo import (
        AppInfo as AppInfoPayload,
        BotAppInfo as BotAppInfoPayload,
        InstallParams as InstallParamsPayload,
        PartialAppInfo as PartialAppInfoPayload,
        Team as TeamPayload,
    )
    from .user import User

__all__ = (
    "PartialAppInfo",
    "AppInfo",
    "BotAppInfo",
    "InstallParams",
)


class InstallParams:
    """Represents the installation parameters for the application, provided by Discord.

    .. versionadded:: 2.5

    Attributes
    ----------
    scopes: List[:class:`str`]
        The scopes requested by the application.
    permissions: :class:`Permissions`
        The permissions requested for the bot role.
    """

    __slots__ = (
        "_app_id",
        "scopes",
        "permissions",
    )

    def __init__(self, data: InstallParamsPayload, parent: AppInfo) -> None:
        self._app_id = parent.id
        self.scopes = data["scopes"]
        self.permissions = Permissions(int(data["permissions"]))

    def __repr__(self) -> str:
        return f"<InstallParams scopes={self.scopes!r} permissions={self.permissions!r}>"

    def to_url(self) -> str:
        """Return a string that can be used to add this application to a server.

        Returns
        -------
        :class:`str`
            The invite url.
        """
        return utils.oauth_url(self._app_id, scopes=self.scopes, permissions=self.permissions)


class PartialAppInfo:
    """Represents partial application information, for example applications in
    game/stream invites in messages.

    .. versionadded:: 2.0

    .. versionchanged:: 2.9
        Moved ``rpc_origins``, ``verify_key``, ``terms_of_service_url``,
        and ``privacy_policy_url`` attributes to the :class:`AppInfo` class instead.
        Added :attr:`cover_image`, and removed deprecated ``summary`` attribute.

    Attributes
    ----------
    id: :class:`int`
        The application's ID.
    name: :class:`str`
        The application's name.
    description: :class:`str`
        The application's description.
    """

    __slots__ = (
        "_state",
        "id",
        "name",
        "description",
        "_icon",
        "_cover_image",
    )

    def __init__(self, *, state: ConnectionState, data: PartialAppInfoPayload):
        self._state: ConnectionState = state

        self.id: int = int(data["id"])
        self.name: str = data["name"]
        self.description: str = data.get("description") or ""
        self._icon: Optional[str] = data.get("icon")
        self._cover_image: Optional[str] = data.get("cover_image")

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} id={self.id}"
            f" name={self.name!r} description={self.description!r}>"
        )

    @property
    def icon(self) -> Optional[Asset]:
        """Optional[:class:`.Asset`]: Retrieves the application's icon asset, if any."""
        if self._icon is None:
            return None
        return Asset._from_icon(self._state, self.id, self._icon, path="app")

    @property
    def cover_image(self) -> Optional[Asset]:
        """Optional[:class:`.Asset`]: Retrieves the application's cover image asset, if any."""
        if self._cover_image is None:
            return None
        return Asset._from_icon(self._state, self.id, self._cover_image, path="app")


class AppInfo(PartialAppInfo):
    """Represents application information, for example applications in invites.

    .. versionadded:: 2.0

    .. versionchanged:: 2.9
        Removed deprecated ``summary`` attribute.

    Attributes
    ----------
    id: :class:`int`
        The application's ID.
    name: :class:`str`
        The application's name.
    description: :class:`str`
        The application's description.
    rpc_origins: List[:class:`str`]
        A list of RPC origin URLs, if RPC is enabled.
    verify_key: :class:`str`
        The hex encoded key for verification in interactions and the
        GameSDK's :ddocs:`GetTicket <game-sdk/applications#getticket>`.
    terms_of_service_url: Optional[:class:`str`]
        The application's terms of service URL, if set.
    privacy_policy_url: Optional[:class:`str`]
        The application's privacy policy URL, if set.
    bot_public: Optional[:class:`bool`]
        Whether the bot can be invited by anyone or if it is locked
        to the application owner.
    bot_require_code_grant: Optional[:class:`bool`]
        Whether the bot requires the completion of the full oauth2 code
        grant flow to join.
    guild_id: Optional[:class:`int`]
        If this application is a game sold on Discord,
        this field will be the guild to which it has been linked to.

        .. versionadded:: 1.3

    primary_sku_id: Optional[:class:`int`]
        If this application is a game sold on Discord,
        this field will be the ID of the "Game SKU" that is created,
        if it exists.

        .. versionadded:: 1.3

    slug: Optional[:class:`str`]
        If this application is a game sold on Discord,
        this field will be the URL slug that links to the store page.

        .. versionadded:: 1.3

    flags: Optional[:class:`ApplicationFlags`]
        The application's public flags.

        .. versionadded:: 2.3

    tags: Optional[List[:class:`str`]]
        The application's tags.

        .. versionadded:: 2.5

    install_params: Optional[:class:`InstallParams`]
        The installation parameters for this application.

        .. versionadded:: 2.5

    custom_install_url: Optional[:class:`str`]
        The custom installation url for this application.

        .. versionadded:: 2.5
    role_connections_verification_url: Optional[:class:`str`]
        The application's role connection verification entry point,
        which when configured will render the app as a verification method
        in the guild role verification configuration.

        .. versionadded:: 2.8
    """

    __slots__ = (
        "rpc_origins",
        "verify_key",
        "terms_of_service_url",
        "privacy_policy_url",
        "bot_public",
        "bot_require_code_grant",
        "guild_id",
        "primary_sku_id",
        "slug",
        "flags",
        "tags",
        "install_params",
        "custom_install_url",
        "role_connections_verification_url",
    )

    def __init__(self, state: ConnectionState, data: AppInfoPayload) -> None:
        super().__init__(state=state, data=data)

        self.verify_key: str = data["verify_key"]

        self.rpc_origins: List[str] = data.get("rpc_origins") or []
        self.terms_of_service_url: Optional[str] = data.get("terms_of_service_url")
        self.privacy_policy_url: Optional[str] = data.get("privacy_policy_url")

        self.bot_public: Optional[bool] = data.get("bot_public")
        self.bot_require_code_grant: Optional[bool] = data.get("bot_require_code_grant")

        self.guild_id: Optional[int] = utils._get_as_snowflake(data, "guild_id")

        self.primary_sku_id: Optional[int] = utils._get_as_snowflake(data, "primary_sku_id")
        self.slug: Optional[str] = data.get("slug")

        flags: Optional[int] = data.get("flags")
        self.flags: Optional[ApplicationFlags] = (
            ApplicationFlags._from_value(flags) if flags is not None else None
        )
        self.tags: Optional[List[str]] = data.get("tags")
        self.install_params: Optional[InstallParams] = (
            InstallParams(data["install_params"], parent=self) if "install_params" in data else None
        )
        self.custom_install_url: Optional[str] = data.get("custom_install_url")
        self.role_connections_verification_url: Optional[str] = data.get(
            "role_connections_verification_url"
        )

    @property
    def guild(self) -> Optional[Guild]:
        """Optional[:class:`Guild`]: If this application is a game sold on Discord,
        this field will be the guild to which it has been linked

        .. versionadded:: 1.3
        """
        return self._state._get_guild(self.guild_id)


class BotAppInfo(AppInfo):
    """Represents the application info for the bot provided by Discord.

    Equivalent to :class:`AppInfo`, but with additional :attr:`owner`
    and :attr:`team` attributes.

    .. versionadded:: 2.9

    Attributes
    ----------
    id: :class:`int`
        The application's ID.
    name: :class:`str`
        The application's name.
    description: :class:`str`
        The application's description.
    rpc_origins: List[:class:`str`]
        A list of RPC origin URLs, if RPC is enabled.
    verify_key: :class:`str`
        The hex encoded key for verification in interactions and the
        GameSDK's :ddocs:`GetTicket <game-sdk/applications#getticket>`.
    terms_of_service_url: Optional[:class:`str`]
        The application's terms of service URL, if set.
    privacy_policy_url: Optional[:class:`str`]
        The application's privacy policy URL, if set.
    bot_public: Optional[:class:`bool`]
        Whether the bot can be invited by anyone or if it is locked
        to the application owner.
    bot_require_code_grant: Optional[:class:`bool`]
        Whether the bot requires the completion of the full oauth2 code
        grant flow to join.
    guild_id: Optional[:class:`int`]
        If this application is a game sold on Discord,
        this field will be the guild to which it has been linked to.
    primary_sku_id: Optional[:class:`int`]
        If this application is a game sold on Discord,
        this field will be the ID of the "Game SKU" that is created,
        if it exists.
    slug: Optional[:class:`str`]
        If this application is a game sold on Discord,
        this field will be the URL slug that links to the store page.
    flags: Optional[:class:`ApplicationFlags`]
        The application's public flags.
    tags: Optional[List[:class:`str`]]
        The application's tags.
    install_params: Optional[:class:`InstallParams`]
        The installation parameters for this application.
    custom_install_url: Optional[:class:`str`]
        The custom installation url for this application.
    role_connections_verification_url: Optional[:class:`str`]
        The application's role connection verification entry point,
        which when configured will render the app as a verification method
        in the guild role verification configuration.
    owner: :class:`User`
        The application's owner.
    team: Optional[:class:`Team`]
        The application's team.
    """

    __slots__ = (
        "owner",
        "team",
    )

    def __init__(self, state: ConnectionState, data: BotAppInfoPayload) -> None:
        super().__init__(state=state, data=data)

        self.owner: User = state.create_user(data["owner"])

        from .team import Team

        team: Optional[TeamPayload] = data.get("team")
        self.team: Optional[Team] = Team(state, team) if team else None

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} id={self.id} name={self.name!r} "
            f"description={self.description!r} public={self.bot_public} "
            f"owner={self.owner!r}>"
        )
