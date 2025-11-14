# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Optional, Union, cast

from ..components import Label as LabelComponent
from ..enums import ComponentType
from ..utils import copy_doc
from .item import UIComponent, ensure_ui_component

if TYPE_CHECKING:
    from typing_extensions import Self

    from ._types import AnySelect
    from .file_upload import FileUpload
    from .text_input import TextInput

    LabelChildUIComponent = Union[TextInput, FileUpload, AnySelect[Any]]

__all__ = ("Label",)


class Label(UIComponent):
    """Represents a UI label.

    This wraps other components with a label and an optional description,
    and can only be used in modals.

    .. versionadded:: 2.11

    Parameters
    ----------
    text: :class:`str`
        The label text.
    component: :class:`TextInput` | :class:`FileUpload` | :class:`BaseSelect`
        The component within the label.
        Currently supports :class:`.ui.TextInput`, :class:`.ui.FileUpload`,
        and select menus (e.g. :class:`.ui.StringSelect`).
    description: :class:`str` | :data:`None`
        The description text for the label.
    id: :class:`int`
        The numeric identifier for the component. Must be unique within a modal.
        This is always present in components received from the API.
        If set to ``0`` (the default) when sending a component, the API will assign
        sequential identifiers to the components in the modal.

    Attributes
    ----------
    text: :class:`str`
        The label text.
    component: :class:`TextInput` | :class:`FileUpload` | :class:`BaseSelect`
        The component within the label.
    description: :class:`str` | :data:`None`
        The description text for the label.
    """

    __repr_attributes__: ClassVar[tuple[str, ...]] = (
        "text",
        "description",
        "component",
    )

    def __init__(
        self,
        text: str,
        component: LabelChildUIComponent,
        *,
        description: Optional[str] = None,
        id: int = 0,
    ) -> None:
        self._id: int = id

        self.text: str = text
        self.description: Optional[str] = description
        self.component: LabelChildUIComponent = ensure_ui_component(component)

    # these are reimplemented here to store the value in a separate attribute,
    # since `Label` lazily constructs `_underlying`, unlike most components
    @property
    @copy_doc(UIComponent.id)
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        self._id = value

    @property
    def _underlying(self) -> LabelComponent:
        return LabelComponent._raw_construct(
            type=ComponentType.label,
            id=self._id,
            text=self.text,
            description=self.description,
            component=self.component._underlying,
        )

    @classmethod
    def from_component(cls, label: LabelComponent) -> Self:
        from .action_row import _to_ui_component

        return cls(
            text=label.text,
            description=label.description,
            component=cast("LabelChildUIComponent", _to_ui_component(label.component)),
            id=label.id,
        )
