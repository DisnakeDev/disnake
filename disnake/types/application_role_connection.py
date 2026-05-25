# SPDX-License-Identifier: MIT

from typing import Literal, TypedDict

from typing_extensions import NotRequired

from .i18n import LocalizationDict

ApplicationRoleConnectionMetadataType = Literal[1, 2, 3, 4, 5, 6, 7, 8]


class ApplicationRoleConnectionMetadata(TypedDict):
    type: ApplicationRoleConnectionMetadataType
    key: str
    name: str
    name_localizations: NotRequired[LocalizationDict]
    description: str
    description_localizations: NotRequired[LocalizationDict]
