# SPDX-License-Identifier: MIT

from __future__ import annotations

import os
from typing import TYPE_CHECKING, ClassVar

from ..components import FileUpload as FileUploadComponent
from ..enums import ComponentType
from ..utils import MISSING
from .item import UIComponent

if TYPE_CHECKING:
    from typing_extensions import Self

__all__ = ("FileUpload",)


class FileUpload(UIComponent):
    """Represents a UI file upload.

    .. versionadded:: |vnext|

    Parameters
    ----------
    custom_id: :class:`str`
        The ID of the file upload that gets received during an interaction.
        If not given then one is generated for you.
    min_values: :class:`int`
        The minimum number of files that must be uploaded.
        Defaults to 1 and must be between 0 and 10.
    max_values: :class:`int`
        The maximum number of files that must be uploaded.
        Defaults to 1 and must be between 1 and 10.
    required: :class:`bool`
        Whether the file upload is required.
        Defaults to ``True``.
    id: :class:`int`
        The numeric identifier for the component. Must be unique within a modal.
        This is always present in components received from the API.
        If set to ``0`` (the default) when sending a component, the API will assign
        sequential identifiers to the components in the modal.
    """

    __repr_attributes__: ClassVar[tuple[str, ...]] = ("min_values", "max_values", "required")
    # We have to set this to MISSING in order to overwrite the abstract property from UIComponent
    _underlying: FileUploadComponent = MISSING

    def __init__(
        self,
        *,
        custom_id: str = MISSING,
        min_values: int = 1,
        max_values: int = 1,
        required: bool = True,
        id: int = 0,
    ) -> None:
        custom_id = os.urandom(16).hex() if custom_id is MISSING else custom_id
        self._underlying = FileUploadComponent._raw_construct(
            type=ComponentType.file_upload,
            id=id,
            custom_id=custom_id,
            min_values=min_values,
            max_values=max_values,
            required=required,
        )

    @property
    def custom_id(self) -> str:
        """:class:`str`: The ID of the file upload that gets received during an interaction."""
        return self._underlying.custom_id

    @custom_id.setter
    def custom_id(self, value: str) -> None:
        self._underlying.custom_id = value

    @property
    def min_values(self) -> int:
        """:class:`int`: The minimum number of files that must be uploaded."""
        return self._underlying.min_values

    @min_values.setter
    def min_values(self, value: int) -> None:
        self._underlying.min_values = int(value)

    @property
    def max_values(self) -> int:
        """:class:`int`: The maximum number of files that must be uploaded."""
        return self._underlying.max_values

    @max_values.setter
    def max_values(self, value: int) -> None:
        self._underlying.max_values = int(value)

    @property
    def required(self) -> bool:
        """:class:`bool`: Whether the select menu is required."""
        return self._underlying.required

    @required.setter
    def required(self, value: bool) -> None:
        self._underlying.required = bool(value)

    @classmethod
    def from_component(cls, file_upload: FileUploadComponent) -> Self:
        return cls(
            custom_id=file_upload.custom_id,
            min_values=file_upload.min_values,
            max_values=file_upload.max_values,
            required=file_upload.required,
            id=file_upload.id,
        )
