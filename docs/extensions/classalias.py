# SPDX-License-Identifier: MIT
from __future__ import annotations

from typing import TYPE_CHECKING

from sphinx.ext.autodoc import ClassDocumenter

if TYPE_CHECKING:
    from sphinx.application import Sphinx

    from ._types import SphinxExtensionMeta


class ClassAliasDocumenter(ClassDocumenter):
    """
    Custom class documenter which documents aliased classes as
    their target, instead of `alias of <x>`.
    """

    objtype = "classalias"
    directivetype = ClassDocumenter.objtype
    priority = -1

    def import_object(self, raiseerror: bool = False) -> bool:
        ret = super().import_object(raiseerror)
        # if imported successfully, force-disable documenting class as module attribute/data
        if ret:
            self.doc_as_attr = False
        return ret


def setup(app: Sphinx) -> SphinxExtensionMeta:
    app.setup_extension("sphinx.ext.autodoc")

    app.add_autodocumenter(ClassAliasDocumenter)

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
