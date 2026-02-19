# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING

from .enums import ApplicationRoleConnectionMetadataType, enum_if_int, try_enum
from .i18n import LocalizationValue, Localized

if TYPE_CHECKING:
    from typing_extensions import Self

    from .i18n import LocalizationProtocol, LocalizedRequired
    from .types.application_role_connection import (
        ApplicationRoleConnectionMetadata as ApplicationRoleConnectionMetadataPayload,
    )


__all__ = ("ApplicationRoleConnectionMetadata",)


class ApplicationRoleConnectionMetadata:
    """Represents the role connection metadata of an application.

    See the :ddocs:`API documentation <resources/application-role-connection-metadata#application-role-connection-metadata-object>`
    for further details and limits.

    The list of metadata records associated with the current application/bot
    can be retrieved/edited using :meth:`Client.fetch_role_connection_metadata`
    and :meth:`Client.edit_role_connection_metadata`.

    .. versionadded:: 2.8

    Attributes
    ----------
    type: :class:`ApplicationRoleConnectionMetadataType`
        The type of the metadata value.
    key: :class:`str`
        The dictionary key for the metadata field.
    name: :class:`str`
        The name of the metadata field.
    name_localizations: :class:`LocalizationValue`
        The localizations for :attr:`name`.
    description: :class:`str`
        The description of the metadata field.
    description_localizations: :class:`LocalizationValue`
        The localizations for :attr:`description`.
    """

    __slots__ = (
        "type",
        "key",
        "name",
        "name_localizations",
        "description",
        "description_localizations",
    )

    def __init__(
        self,
        *,
        type: ApplicationRoleConnectionMetadataType,
        key: str,
        name: LocalizedRequired,
        description: LocalizedRequired,
    ) -> None:
        self.type: ApplicationRoleConnectionMetadataType = enum_if_int(
            ApplicationRoleConnectionMetadataType, type
        )
        self.key: str = key

        name_loc = Localized._cast(name, True)
        self.name: str = name_loc.string
        self.name_localizations: LocalizationValue = name_loc.localizations

        desc_loc = Localized._cast(description, True)
        self.description: str = desc_loc.string
        self.description_localizations: LocalizationValue = desc_loc.localizations

    def __repr__(self) -> str:
        return (
            f"<ApplicationRoleConnectionMetadata name={self.name!r} key={self.key!r} "
            f"description={self.description!r} type={self.type!r}>"
        )

    @classmethod
    def _from_data(cls, data: ApplicationRoleConnectionMetadataPayload) -> Self:
        return cls(
            type=try_enum(ApplicationRoleConnectionMetadataType, data["type"]),
            key=data["key"],
            name=Localized(data["name"], data=data.get("name_localizations")),
            description=Localized(data["description"], data=data.get("description_localizations")),
        )

    def to_dict(self) -> ApplicationRoleConnectionMetadataPayload:
        data: ApplicationRoleConnectionMetadataPayload = {
            "type": self.type.value,
            "key": self.key,
            "name": self.name,
            "description": self.description,
        }

        if (loc := self.name_localizations.data) is not None:
            data["name_localizations"] = loc
        if (loc := self.description_localizations.data) is not None:
            data["description_localizations"] = loc

        return data

    def _localize(self, store: LocalizationProtocol) -> None:
        self.name_localizations._link(store)
        self.description_localizations._link(store)
