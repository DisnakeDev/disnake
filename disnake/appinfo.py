# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, cast

from . import utils
from .asset import Asset, AssetBytes
from .enums import ApplicationEventWebhookStatus, try_enum
from .flags import ApplicationFlags
from .permissions import Permissions
from .utils import MISSING

if TYPE_CHECKING:
    from .guild import Guild
    from .state import ConnectionState
    from .types.appinfo import (
        AppInfo as AppInfoPayload,
        ApplicationIntegrationType as ApplicationIntegrationTypeLiteral,
        ApplicationIntegrationTypeConfiguration as ApplicationIntegrationTypeConfigurationPayload,
        EditAppInfo as EditAppInfoPayload,
        InstallParams as InstallParamsPayload,
        PartialAppInfo as PartialAppInfoPayload,
        Team as TeamPayload,
    )
    from .user import User


__all__ = (
    "AppInfo",
    "PartialAppInfo",
    "InstallParams",
    "InstallTypeConfiguration",
)


class InstallParams:
    """Represents the installation parameters for the application, provided by Discord.

    .. versionadded:: 2.5

    .. versionchanged:: 2.11
        This class can now be created by users.

    Attributes
    ----------
    scopes: List[:class:`str`]
        The scopes requested by the application.
    permissions: :class:`Permissions`
        The permissions requested for the bot role.
    """

    __slots__ = (
        "_app_id",
        "_install_type",
        "scopes",
        "permissions",
    )

    def __init__(
        self,
        *,
        scopes: List[str],
        permissions: Permissions,
    ) -> None:
        self.scopes = scopes
        self.permissions = permissions
        self._app_id: int = 0
        self._install_type: Optional[ApplicationIntegrationTypeLiteral] = None

    @classmethod
    def _from_data(
        cls,
        data: InstallParamsPayload,
        parent: AppInfo,
        *,
        install_type: Optional[ApplicationIntegrationTypeLiteral] = None,
    ) -> InstallParams:
        instance = cls(permissions=Permissions(int(data["permissions"])), scopes=data["scopes"])
        instance._install_type = install_type
        instance._app_id = parent.id
        return instance

    def __repr__(self) -> str:
        return f"<InstallParams scopes={self.scopes!r} permissions={self.permissions!r}>"

    def to_url(self) -> str:
        """Returns a string that can be used to install this application.

        .. note:: This method can only be used on InstallParams that have been created by :meth:`.Client.application_info`

        Returns
        -------
        :class:`str`
            The invite url.
        """
        if not self._app_id:
            raise ValueError("This InstallParams instance is not linked to an application.")
        return utils.oauth_url(
            self._app_id,
            scopes=self.scopes,
            permissions=self.permissions,
            integration_type=(
                self._install_type if self._install_type is not None else utils.MISSING
            ),
        )

    def to_dict(self) -> InstallParamsPayload:
        return {
            "scopes": self.scopes,
            "permissions": str(self.permissions.value),
        }


class InstallTypeConfiguration:
    """Represents the configuration for a particular application installation type.

    .. versionadded:: 2.10

    .. versionchanged:: 2.11

        This class can now be created by users.

    Attributes
    ----------
    install_params: Optional[:class:`InstallParams`]
        The parameters for this installation type.
    """

    __slots__ = ("install_params",)

    def __init__(self, *, install_params: Optional[InstallParams] = None) -> None:
        self.install_params: Optional[InstallParams] = install_params

    @classmethod
    def _from_data(
        cls,
        data: ApplicationIntegrationTypeConfigurationPayload,
        *,
        parent: AppInfo,
        install_type: ApplicationIntegrationTypeLiteral,
    ) -> InstallTypeConfiguration:
        return cls(
            install_params=InstallParams._from_data(
                install_params, parent=parent, install_type=install_type
            )
            if (install_params := data.get("oauth2_install_params"))
            else None
        )

    def to_dict(self) -> ApplicationIntegrationTypeConfigurationPayload:
        payload: ApplicationIntegrationTypeConfigurationPayload = {}
        if self.install_params:
            payload["oauth2_install_params"] = self.install_params.to_dict()
        return payload


class AppInfo:
    """Represents the application info for the bot provided by Discord.

    Attributes
    ----------
    id: :class:`int`
        The application's ID.
    name: :class:`str`
        The application's name.
    owner: :class:`User`
        The application's owner.
    team: Optional[:class:`Team`]
        The application's team.

        .. versionadded:: 1.3

    description: :class:`str`
        The application's description.
    bot_public: :class:`bool`
        Whether the bot can be invited by anyone or if it is locked
        to the application owner.
    bot_require_code_grant: :class:`bool`
        Whether the bot requires the completion of the full oauth2 code
        grant flow to join.
    rpc_origins: Optional[List[:class:`str`]]
        A list of RPC origin URLs, if RPC is enabled.
    verify_key: :class:`str`
        The hex encoded key for verification in interactions and the
        GameSDK's :ddocs:`GetTicket <game-sdk/applications#getticket>`.

        .. versionadded:: 1.3

    guild_id: Optional[:class:`int`]
        The ID of the guild associated with the application, if any.

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

    terms_of_service_url: Optional[:class:`str`]
        The application's terms of service URL, if set.

        .. versionadded:: 2.0

    privacy_policy_url: Optional[:class:`str`]
        The application's privacy policy URL, if set.

        .. versionadded:: 2.0

    flags: Optional[:class:`ApplicationFlags`]
        The application's public flags.

        .. versionadded:: 2.3

    tags: Optional[List[:class:`str`]]
        The application's tags.

        .. versionadded:: 2.5

    install_params: Optional[:class:`InstallParams`]
        The installation parameters for this application.

        See also :attr:`guild_install_type_config`/:attr:`user_install_type_config`
        for installation type-specific configuration.

        .. versionadded:: 2.5

    custom_install_url: Optional[:class:`str`]
        The custom installation url for this application.

        .. versionadded:: 2.5
    role_connections_verification_url: Optional[:class:`str`]
        The application's role connection verification entry point,
        which when configured will render the app as a verification method
        in the guild role verification configuration.

        .. versionadded:: 2.8
    approximate_guild_count: :class:`int`
        The approximate number of guilds the application is installed to.

        .. versionadded:: 2.10
    approximate_user_install_count: :class:`int`
        The approximate number of users that have installed the application
        (for user-installable apps).

        .. versionadded:: 2.10

    approximate_user_authorization_count: :class:`int`
        The approximate number of users that have authorized the app with OAuth2.

        .. versionadded:: 2.11
    redirect_uris: Optional[List[:class:`str`]]
        The application's OAuth2 redirect URIs.

        .. versionadded:: 2.11

    interactions_endpoint_url: Optional[:class:`str`]
        The application's interactions endpoint URL.

        .. versionadded:: 2.11

    event_webhooks_url: Optional[:class:`str`]
        The application's event webhooks URL.

        .. versionadded:: 2.11

    event_webhooks_status: :class:`ApplicationEventWebhookStatus`
        The application's event webhooks status.

        .. versionadded:: 2.11

    event_webhooks_types: Optional[List[:class:`str`]]
        The application's event webhook types, if any.

        .. versionadded:: 2.11
    """

    __slots__ = (
        "_state",
        "description",
        "id",
        "name",
        "rpc_origins",
        "bot_public",
        "bot_require_code_grant",
        "owner",
        "_icon",
        "_summary",
        "verify_key",
        "team",
        "guild_id",
        "primary_sku_id",
        "slug",
        "_cover_image",
        "terms_of_service_url",
        "privacy_policy_url",
        "flags",
        "tags",
        "install_params",
        "redirect_uris",
        "custom_install_url",
        "interactions_endpoint_url",
        "role_connections_verification_url",
        "event_webhooks_url",
        "event_webhooks_status",
        "event_webhooks_types",
        "approximate_guild_count",
        "approximate_user_install_count",
        "approximate_user_authorization_count",
        "_install_types_config",
    )

    def __init__(self, state: ConnectionState, data: AppInfoPayload) -> None:
        from .team import Team

        self._state: ConnectionState = state
        self.id: int = int(data["id"])
        self.name: str = data["name"]
        self.description: str = data["description"]
        self._icon: Optional[str] = data["icon"]
        self.rpc_origins: List[str] = data.get("rpc_origins") or []
        self.bot_public: bool = data["bot_public"]
        self.bot_require_code_grant: bool = data["bot_require_code_grant"]
        self.owner: User = state.create_user(data["owner"])

        team: Optional[TeamPayload] = data.get("team")
        self.team: Optional[Team] = Team(state, team) if team else None

        self._summary: str = data.get("summary", "")
        self.verify_key: str = data["verify_key"]

        self.guild_id: Optional[int] = utils._get_as_snowflake(data, "guild_id")

        self.primary_sku_id: Optional[int] = utils._get_as_snowflake(data, "primary_sku_id")
        self.slug: Optional[str] = data.get("slug")
        self._cover_image: Optional[str] = data.get("cover_image")
        self.terms_of_service_url: Optional[str] = data.get("terms_of_service_url")
        self.privacy_policy_url: Optional[str] = data.get("privacy_policy_url")

        flags: Optional[int] = data.get("flags")
        self.flags: Optional[ApplicationFlags] = (
            ApplicationFlags._from_value(flags) if flags is not None else None
        )
        self.tags: Optional[List[str]] = data.get("tags")
        self.install_params: Optional[InstallParams] = (
            InstallParams._from_data(data["install_params"], parent=self)
            if "install_params" in data
            else None
        )
        self.custom_install_url: Optional[str] = data.get("custom_install_url")
        self.redirect_uris: Optional[List[str]] = data.get("redirect_uris")
        self.interactions_endpoint_url: Optional[str] = data.get("interactions_endpoint_url")
        self.role_connections_verification_url: Optional[str] = data.get(
            "role_connections_verification_url"
        )
        self.event_webhooks_url: Optional[str] = data.get("event_webhooks_url")
        self.event_webhooks_status: ApplicationEventWebhookStatus = try_enum(
            ApplicationEventWebhookStatus, data.get("event_webhooks_status", 1)
        )
        self.event_webhooks_types: Optional[List[str]] = data.get("event_webhooks_types")
        self.approximate_guild_count: int = data.get("approximate_guild_count", 0)
        self.approximate_user_install_count: int = data.get("approximate_user_install_count", 0)
        self.approximate_user_authorization_count: int = data.get(
            "approximate_user_authorization_count", 0
        )

        # this is a bit of a mess, but there's no better way to expose this data for now
        self._install_types_config: Dict[
            ApplicationIntegrationTypeLiteral, InstallTypeConfiguration
        ] = {}
        for type_str, config in (data.get("integration_types_config") or {}).items():
            install_type = cast("ApplicationIntegrationTypeLiteral", int(type_str))
            self._install_types_config[install_type] = InstallTypeConfiguration._from_data(
                config or {},
                parent=self,
                install_type=install_type,
            )

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} id={self.id} name={self.name!r} "
            f"description={self.description!r} public={self.bot_public} "
            f"owner={self.owner!r}>"
        )

    @property
    def icon(self) -> Optional[Asset]:
        """Optional[:class:`.Asset`]: Retrieves the application's icon asset, if any."""
        if self._icon is None:
            return None
        return Asset._from_icon(self._state, self.id, self._icon, path="app")

    @property
    def cover_image(self) -> Optional[Asset]:
        """Optional[:class:`.Asset`]: Retrieves the rich presence cover image asset, if any."""
        if self._cover_image is None:
            return None
        return Asset._from_cover_image(self._state, self.id, self._cover_image)

    @property
    def guild(self) -> Optional[Guild]:
        """Optional[:class:`Guild`]: The guild associated with the application, if any.

        .. versionadded:: 1.3
        """
        return self._state._get_guild(self.guild_id)

    @property
    def summary(self) -> str:
        """:class:`str`: If this application is a game sold on Discord,
        this field will be the summary field for the store page of its primary SKU.

        .. versionadded:: 1.3

        .. deprecated:: 2.5

            This field is deprecated by discord and is now always blank. Consider using :attr:`.description` instead.
        """
        utils.warn_deprecated(
            "summary is deprecated and will be removed in a future version. Consider using description instead.",
            stacklevel=2,
        )
        return self._summary

    @property
    def guild_install_type_config(self) -> Optional[InstallTypeConfiguration]:
        """Optional[:class:`InstallTypeConfiguration`]: The guild installation parameters for
        this application. If this application cannot be installed to guilds, returns ``None``.

        .. versionadded:: 2.10
        """
        return self._install_types_config.get(0)

    @property
    def user_install_type_config(self) -> Optional[InstallTypeConfiguration]:
        """Optional[:class:`InstallTypeConfiguration`]: The user installation parameters for
        this application. If this application cannot be installed to users, returns ``None``.

        .. versionadded:: 2.10
        """
        return self._install_types_config.get(1)

    async def edit(
        self,
        *,
        custom_install_url: Optional[str] = MISSING,
        description: Optional[str] = MISSING,
        role_connections_verification_url: Optional[str] = MISSING,
        install_params: Optional[InstallParams] = MISSING,
        guild_install_type_config: InstallTypeConfiguration = MISSING,
        user_install_type_config: InstallTypeConfiguration = MISSING,
        flags: ApplicationFlags = MISSING,
        icon: Optional[AssetBytes] = MISSING,
        cover_image: Optional[AssetBytes] = MISSING,
        interactions_endpoint_url: Optional[str] = MISSING,
        tags: Sequence[str] = MISSING,
        event_webhooks_url: Optional[str] = MISSING,
        event_webhooks_status: ApplicationEventWebhookStatus = MISSING,
        event_webhooks_types: Sequence[str] = MISSING,
        **kwargs,
    ) -> AppInfo:
        """|coro|

        Edit's the application's information.

        All parameters are optional.

        .. versionadded:: 2.11

        Parameters
        ----------
        description: Optional[:class:`str`]
            The application's description.
        flags: Optional[:class:`ApplicationFlags`]
            The application's public flags.

            This is restricted to only affecting the limited intent flags:
            :attr:`~ApplicationFlags.gateway_guild_members_limited`,
            :attr:`~ApplicationFlags.gateway_presence_limited`, and
            :attr:`~ApplicationFlags.gateway_message_content_limited`.

            .. warning::
                Disabling an intent that you are currently requesting during your current session
                will cause you to be disconnected from the gateway. Take caution when providing this parameter.

        tags: Optional[List[:class:`str`]]
            The application's tags.
        install_params: Optional[:class:`InstallParams`]
            The installation parameters for this application.

            Cannot be provided with ``custom_install_url``.
        custom_install_url: Optional[:class:`str`]
            The custom installation url for this application.
        role_connections_verification_url: Optional[:class:`str`]
            The application's role connection verification entry point,
            which when configured will render the app as a verification method
            in the guild role verification configuration.
        interactions_endpoint_url: Optional[:class:`str`]
            The application's interactions endpoint URL.
        icon: Optional[|resource_type|]
            Update the application's icon asset, if any.
        cover_image: Optional[|resource_type|]
            Update the cover_image for rich presence integrations.
        guild_install_type_config: Optional[:class:`InstallTypeConfiguration`]
            The guild installation type configuration for this application.
        user_install_type_config: Optional[:class:`InstallTypeConfiguration`]
            The user installation type configuration for this application.
        event_webhooks_url: Optional[:class:`str`]
            The application's event webhooks URL.
        event_webhooks_status: :class:`ApplicationEventWebhookStatus`
            The application's event webhooks status.
        event_webhook_types: Optional[List]
            The application's event webhook types. See `webhook event types <https://discord.com/developers/docs/events/webhook-events#event-types>`_
            for a list of valid events.

        Raises
        ------
        HTTPException
            Editing the application information failed.

        Returns
        -------
        :class:`.AppInfo`
            The new application information.
        """
        fields: EditAppInfoPayload = {}

        if install_params is not MISSING:
            fields["install_params"] = (
                install_params.to_dict() if install_params is not None else None
            )

        if guild_install_type_config is not MISSING or user_install_type_config is not MISSING:
            integration_types_config: Dict[
                ApplicationIntegrationTypeLiteral, ApplicationIntegrationTypeConfigurationPayload
            ] = {}

            if guild_install_type_config is not MISSING:
                integration_types_config[0] = guild_install_type_config.to_dict()
            elif self.guild_install_type_config:
                integration_types_config[0] = self.guild_install_type_config.to_dict()

            if user_install_type_config is not MISSING:
                integration_types_config[1] = user_install_type_config.to_dict()
            elif self.user_install_type_config:
                integration_types_config[1] = self.user_install_type_config.to_dict()

            fields["integration_types_config"] = integration_types_config

        if icon is not MISSING:
            fields["icon"] = await utils._assetbytes_to_base64_data(icon)

        if cover_image is not MISSING:
            fields["cover_image"] = await utils._assetbytes_to_base64_data(cover_image)

        if flags is not MISSING:
            fields["flags"] = flags.value

        if description is not MISSING:
            fields["description"] = description or ""

        if custom_install_url is not MISSING:
            fields["custom_install_url"] = custom_install_url

        if role_connections_verification_url is not MISSING:
            fields["role_connections_verification_url"] = role_connections_verification_url

        if interactions_endpoint_url is not MISSING:
            fields["interactions_endpoint_url"] = interactions_endpoint_url

        if event_webhooks_url is not MISSING:
            fields["event_webhooks_url"] = event_webhooks_url

        if event_webhooks_status is not MISSING:
            if event_webhooks_status is ApplicationEventWebhookStatus.disabled_by_discord:
                raise TypeError(f"cannot set 'event_webhooks_status' to {event_webhooks_status!r}")
            fields["event_webhooks_status"] = event_webhooks_status.value

        if event_webhooks_types is not MISSING:
            fields["event_webhooks_types"] = list(event_webhooks_types)

        if tags is not MISSING:
            fields["tags"] = list(tags) if tags else None

        if kwargs:
            fields.update(**kwargs)  # type: ignore

        data = await self._state.http.edit_application_info(**fields)
        return AppInfo(self._state, data)


class PartialAppInfo:
    """Represents a partial AppInfo given by :func:`~disnake.abc.GuildChannel.create_invite`.

    .. versionadded:: 2.0

    Attributes
    ----------
    id: :class:`int`
        The application's ID.
    name: :class:`str`
        The application's name.
    description: :class:`str`
        The application's description.
    rpc_origins: Optional[List[:class:`str`]]
        A list of RPC origin URLs, if RPC is enabled.
    verify_key: :class:`str`
        The hex encoded key for verification in interactions and the
        GameSDK's :ddocs:`GetTicket <game-sdk/applications#getticket>`.
    terms_of_service_url: Optional[:class:`str`]
        The application's terms of service URL, if set.
    privacy_policy_url: Optional[:class:`str`]
        The application's privacy policy URL, if set.
    """

    __slots__ = (
        "_state",
        "id",
        "name",
        "description",
        "rpc_origins",
        "_summary",
        "verify_key",
        "terms_of_service_url",
        "privacy_policy_url",
        "_icon",
    )

    def __init__(self, *, state: ConnectionState, data: PartialAppInfoPayload) -> None:
        self._state: ConnectionState = state
        self.id: int = int(data["id"])
        self.name: str = data["name"]
        self._icon: Optional[str] = data.get("icon")
        self.description: str = data["description"]
        self.rpc_origins: Optional[List[str]] = data.get("rpc_origins")
        self._summary: str = data.get("summary", "")
        self.verify_key: str = data["verify_key"]
        self.terms_of_service_url: Optional[str] = data.get("terms_of_service_url")
        self.privacy_policy_url: Optional[str] = data.get("privacy_policy_url")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} name={self.name!r} description={self.description!r}>"

    @property
    def icon(self) -> Optional[Asset]:
        """Optional[:class:`.Asset`]: Retrieves the application's icon asset, if any."""
        if self._icon is None:
            return None
        return Asset._from_icon(self._state, self.id, self._icon, path="app")

    @property
    def summary(self) -> str:
        """:class:`str`: If this application is a game sold on Discord,
        this field will be the summary field for the store page of its primary SKU.

        .. deprecated:: 2.5

            This field is deprecated by discord and is now always blank. Consider using :attr:`.description` instead.
        """
        utils.warn_deprecated(
            "summary is deprecated and will be removed in a future version. Consider using description instead.",
            stacklevel=2,
        )
        return self._summary
