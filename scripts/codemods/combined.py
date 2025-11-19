# SPDX-License-Identifier: MIT
from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from libcst import codemod

from . import link_doc_types, overloads_no_missing, typed_flags, typed_permissions
from .base import NoMetadataWrapperMixin

if TYPE_CHECKING:
    import libcst as cst

CODEMODS = [
    overloads_no_missing.EllipsisOverloads,
    typed_flags.FlagTypings,
    typed_permissions.PermissionTypings,
    link_doc_types.DocstringTransformer,
]


# translate `codemod.SkipFile` into a graceful return
def wrap_translate_skipfile(func):
    @functools.wraps(func)
    def wrap(self: codemod.Codemod, tree: cst.Module) -> cst.Module:
        try:
            return func(self, tree)
        except codemod.SkipFile:
            return tree

    return wrap


class CombinedCodemod(NoMetadataWrapperMixin, codemod.MagicArgsCodemodCommand):
    DESCRIPTION = "Runs all custom codemods from this repo."

    def get_transforms(self):
        # yield codemods to be run, while monkeypatching `transform_module`
        for codemod_type in CODEMODS:
            yield type(
                f"{codemod_type.__name__}__Wrapped",
                (codemod_type,),
                {"transform_module": wrap_translate_skipfile(codemod_type.transform_module)},
            )
