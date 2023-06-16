# SPDX-License-Identifier: MIT

import contextlib
from abc import ABC
from typing import ClassVar, Optional

import libcst as cst
import libcst.codemod as codemod


class NoMetadataWrapperMixin:
    # stub the metadata wrapper, which deepcopies the entire module on initialization
    # (`unsafe_skip_copy` exists but it can't be set in the general case)
    # (I think this should be fine?)
    _handle_metadata_reference = contextlib.nullcontext


# similar to `VisitorBasedCodemodCommand`,
# except without the `MatcherDecoratableTransformer` base for performance reasons
class BaseCodemodCommand(NoMetadataWrapperMixin, cst.CSTTransformer, codemod.CodemodCommand, ABC):
    CHECK_MARKER: ClassVar[Optional[str]] = None

    def transform_module(self, tree: cst.Module) -> cst.Module:
        if self.CHECK_MARKER:
            assert self.context.filename

            # n.b. doing it this way is faster than using `tree.code`,
            # which codegen's the entire module again
            with open(self.context.filename, "r", encoding="utf-8") as f:
                code = f.read()

            if self.CHECK_MARKER not in code:
                raise codemod.SkipFile(
                    f"this module does not contain the required marker: `{self.CHECK_MARKER}`."
                )

        return super().transform_module(tree)

    # trivial implementation, identical to `ContextAwareTransformer`
    def transform_module_impl(self, tree: cst.Module) -> cst.Module:
        return tree.visit(self)
