# SPDX-License-Identifier: MIT

import contextlib
from abc import ABC

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
    # trivial implementation, identical to `ContextAwareTransformer`
    def transform_module_impl(self, tree: cst.Module) -> cst.Module:
        return tree.visit(self)
