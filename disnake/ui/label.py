# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Optional, Tuple, Union, cast

from ..components import Label as LabelComponent
from ..enums import ComponentType
from ..utils import copy_doc
from .item import UIComponent, ensure_ui_component

if TYPE_CHECKING:
    from typing_extensions import Self

    from .select.string import StringSelect
    from .text_input import TextInput

    LabelChildUIComponent = Union[TextInput, StringSelect[Any]]

__all__ = ("Label",)


class Label(UIComponent):
    """Represents a UI label.

    This wraps other components with a label and an optional description,
    and can only be used in modals.

    .. versionadded:: 2.11

    Parameters
    ----------
    label: :class:`str`
        The label text.
    component: Union[:class:`TextInput`, :class:`StringSelectMenu`]
        The component within the label.
    description: Optional[:class:`str`]
        The description text for the label.
    id: :class:`int`
        The numeric identifier for the component. Must be unique within the message.
        If set to ``0`` (the default) when sending a component, the API will assign
        sequential identifiers to the components in the message.

    Attributes
    ----------
    label: :class:`str`
        The label text.
    component: Union[:class:`TextInput`, :class:`StringSelectMenu`]
        The component within the label.
    description: Optional[:class:`str`]
        The description text for the label.
    """

    __repr_attributes__: ClassVar[Tuple[str, ...]] = (
        "label",
        "description",
        "component",
    )

    def __init__(
        self,
        label: str,
        component: LabelChildUIComponent,
        *,
        description: Optional[str] = None,
        id: int = 0,
    ) -> None:
        self._id: int = id

        self.label: str = label
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
            label=self.label,
            description=self.description,
            component=self.component._underlying,
        )

    @classmethod
    def from_component(cls, section: LabelComponent) -> Self:
        from .action_row import _to_ui_component

        return cls(
            label=section.label,
            description=section.description,
            component=cast("LabelChildUIComponent", _to_ui_component(section.component)),
        )
