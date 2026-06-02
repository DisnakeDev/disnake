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


# show `Enum.name` instead of `(name, value)` in signatures
# (object_description has a special case for enum.Enum, but obviously not
# for our custom enum types, which ultimately get displayed as plain tuples)
def _patch_object_description() -> None:
    from sphinx.util import inspect

    orig_description = inspect.object_description

    def patched_description(obj: Any, **kwargs: Any) -> Any:
        if isinstance(obj, disnake.enums._EnumValueBase):
            # bypass `__str__` defined on some enums
            return disnake.enums._EnumValueBase.__str__(obj)
        return orig_description(obj, **kwargs)

    inspect.object_description = patched_description


def setup(app: Sphinx) -> SphinxExtensionMeta:
    app.setup_extension("sphinx.ext.autodoc")

    app.add_autodocumenter(EnumMemberDocumenter)

    _patch_object_description()

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
