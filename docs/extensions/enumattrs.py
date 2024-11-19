# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sphinx.ext.autodoc import AttributeDocumenter

import disnake

if TYPE_CHECKING:
    from sphinx.application import Sphinx

    from ._types import SphinxExtensionMeta


class EnumMemberDocumenter(AttributeDocumenter):
    """
    Custom enum member documenter which hides enum values.
    Gets used automatically for all `_EnumValueBase` instances.
    """

    objtype = "enumattribute"
    directivetype = AttributeDocumenter.objtype
    priority = 10 + AttributeDocumenter.priority

    @classmethod
    def can_document_member(cls, member: Any, membername: str, isattr: bool, parent: Any) -> bool:
        return super().can_document_member(member, membername, isattr, parent) and isinstance(
            member, disnake.enums._EnumValueBase
        )

    def should_suppress_value_header(self) -> bool:
        # always hide enum member values
        return True


def setup(app: Sphinx) -> SphinxExtensionMeta:
    app.setup_extension("sphinx.ext.autodoc")

    app.add_autodocumenter(EnumMemberDocumenter)

    # show `Enum.name` instead of `<Enum.name: 123>` in signatures
    disnake.enums._EnumValueBase.__repr__ = disnake.enums._EnumValueBase.__str__

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
