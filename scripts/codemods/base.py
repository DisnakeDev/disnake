# SPDX-License-Identifier: MIT

from abc import ABC
from contextlib import contextmanager
from contextvars import ContextVar
from typing import TYPE_CHECKING, ClassVar, Optional

import libcst as cst
import libcst.codemod as codemod

if TYPE_CHECKING:
    base_type = codemod.Codemod
else:
    base_type = object

ctx_unsafe_skip_copy = ContextVar("ctx_unsafe_skip_copy", default=False)


class NoMetadataWrapperMixin(base_type):
    # Tag type for the metadata wrapper, which prevents it from
    # deepcopying the entire module on initialization

    @contextmanager
    def _handle_metadata_reference(self, tree: cst.Module):
        ctx_unsafe_skip_copy.set(True)
        with super()._handle_metadata_reference(tree) as res:
            ctx_unsafe_skip_copy.set(False)
            yield res


def patched_init(*args, _orig=cst.MetadataWrapper.__init__, **kwargs):
    if ctx_unsafe_skip_copy.get():
        kwargs["unsafe_skip_copy"] = True
    return _orig(*args, **kwargs)


cst.MetadataWrapper.__init__ = patched_init


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
