# SPDX-License-Identifier: MIT
"""Update docstrings to use pep 585 and pep 602 style type hints for documentation."""

import libcst as cst
from libcst import matchers as m

from ..new_typehints import apply_replacements
from .base import BaseCodemodCommand


class DocstringTransformer(BaseCodemodCommand):
    DESCRIPTION = "Replace type hints in docstrings with PEP 585/604 style."

    def _replace_simple_string(self, simple_string: cst.SimpleString) -> cst.SimpleString:
        # simple_string.value is the literal including quotes and prefixes
        current = simple_string.raw_value
        prefix = simple_string.prefix

        new_inner = apply_replacements(current, include_backslash=True)
        # TODO: enable D301 and raw docstrings
        # if r"\\" in new_inner:
        #     prefix = "r"
        #     new_inner = new_inner.replace(r"\\", "\\")
        new_value = f"{prefix}{simple_string.quote}{new_inner}{simple_string.quote}"
        return simple_string.with_changes(value=new_value)

    def _maybe_replace_first_stmt(self, stmts):
        # stmts is a list of BaseStatement
        if not stmts:
            return stmts
        first = stmts[0]
        # Match a simple top-level statement that is a docstring: a SimpleStatementLine
        # whose first expression is a SimpleString.
        if m.matches(first, m.SimpleStatementLine(body=[m.Expr(value=m.SimpleString())])):
            expr = first.body[0]
            new_string = self._replace_simple_string(expr.value)
            new_expr = expr.with_changes(value=new_string)
            new_first = first.with_changes(body=[new_expr])
            return [new_first, *stmts[1:]]
        return stmts

    def leave_Module(self, original: cst.Module, updated: cst.Module) -> cst.Module:
        new_body = self._maybe_replace_first_stmt(updated.body)
        if new_body is not updated.body:
            return updated.with_changes(body=new_body)
        return updated

    def _replace_indented_block(self, block: cst.BaseSuite) -> cst.BaseSuite:
        # Only IndentedBlock has a .body attribute we can modify.
        if isinstance(block, cst.IndentedBlock):
            new_stmts = self._maybe_replace_first_stmt(block.body)
            if new_stmts is not block.body:
                return block.with_changes(body=new_stmts)
        return block

    def leave_ClassDef(self, original: cst.ClassDef, updated: cst.ClassDef) -> cst.ClassDef:
        new_body = self._replace_indented_block(updated.body)
        if new_body is not updated.body:
            return updated.with_changes(body=new_body)
        return updated

    def leave_FunctionDef(
        self, original: cst.FunctionDef, updated: cst.FunctionDef
    ) -> cst.FunctionDef:
        new_body = self._replace_indented_block(updated.body)
        if new_body is not updated.body:
            return updated.with_changes(body=new_body)
        return updated

    def leave_AsyncFunctionDef(self, original, updated):
        new_body = self._replace_indented_block(updated.body)
        if new_body is not updated.body:
            return updated.with_changes(body=new_body)
        return updated
