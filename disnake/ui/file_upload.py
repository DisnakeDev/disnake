# SPDX-License-Identifier: MIT

from __future__ import annotations

import os
from collections.abc import Sequence
from typing import TYPE_CHECKING, ClassVar, Literal

from ..components import FileUpload as FileUploadComponent
from ..enums import ComponentType
from ..utils import MISSING
from .item import UIComponent

if TYPE_CHECKING:
    from typing_extensions import Self

__all__ = ("FileUpload",)


class FileUpload(UIComponent):
    r"""Represents a UI file upload.

    .. versionadded:: 2.12

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
    file_types: :class:`~collections.abc.Sequence`\[:class:`str`] | :data:`None`
        A list of file types that can be uploaded with this component.
        Allowed values are ``image``, ``video``, and ``audio``, as well as
        any dot-prefixed extension such as ``.pdf`` (up to 10).
        Defaults to all types (i.e. :data:`None`).

        .. versionadded:: |vnext|

        .. warning::
            Note that only the extension of filenames is checked, the actual contents of files
            are not inspected and may not actually match the extension.
            It is up to you to ensure the file is valid, if necessary.

    id: :class:`int`
        The numeric identifier for the component. Must be unique within a modal.
        This is always present in components received from the API.
        If set to ``0`` (the default) when sending a component, the API will assign
        sequential identifiers to the components in the modal.
    """

    __repr_attributes__: ClassVar[tuple[str, ...]] = (
        "min_values",
        "max_values",
        "required",
        "file_types",
    )
    # We have to set this to MISSING in order to overwrite the abstract property from UIComponent
    _underlying: FileUploadComponent = MISSING

    def __init__(
        self,
        *,
        custom_id: str = MISSING,
        min_values: int = 1,
        max_values: int = 1,
        required: bool = True,
        file_types: Sequence[Literal["image", "video", "audio"] | str] | None = None,
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
            file_types=file_types,
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
        """:class:`bool`: Whether the file upload is required."""
        return self._underlying.required

    @required.setter
    def required(self, value: bool) -> None:
        self._underlying.required = bool(value)

    @property
    def file_types(self) -> Sequence[Literal["image", "video", "audio"] | str] | None:
        r""":class:`~collections.abc.Sequence`\[:class:`str`] | :data:`None`: A list of file types that can be uploaded with this component.

        .. versionadded:: |vnext|
        """
        return self._underlying.file_types

    @file_types.setter
    def file_types(self, value: Sequence[Literal["image", "video", "audio"] | str] | None) -> None:
        if value is not None and (
            not isinstance(value, Sequence)
            or isinstance(value, str)
            or not all(isinstance(obj, str) for obj in value)
        ):
            msg = "file_types must be a list/sequence of `str`s"
            raise TypeError(msg)

        self._underlying.file_types = value

    @classmethod
    def from_component(cls, file_upload: FileUploadComponent) -> Self:
        return cls(
            custom_id=file_upload.custom_id,
            min_values=file_upload.min_values,
            max_values=file_upload.max_values,
            required=file_upload.required,
            file_types=file_upload.file_types,
            id=file_upload.id,
        )
