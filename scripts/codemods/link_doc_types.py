# SPDX-License-Identifier: MIT
"""Update docstrings to use pep 585 and pep 602 style type hints for documentation."""

import re

import libcst as cst
from libcst import matchers as m

from .base import BaseCodemodCommand

CONTAINERS = {
    "Dict": "dict",
    "List": "list",
    "Set": "set",
    "Tuple": "tuple",
    "FrozenSet": "frozenset",
    "Sequence": "collections.abc.Sequence",
    "Mapping": "collections.abc.Mapping",
    "Callable": "collections.abc.Callable",
    "Collection": "collections.abc.Collection",
    "Coroutine": "collections.abc.Coroutine",
    "AsyncGenerator": "collections.abc.AsyncGenerator",
    "AsyncIterable": "collections.abc.AsyncIterable",
    "Awaitable": "collections.abc.Awaitable",
    "Iterable": "collections.abc.Iterable",
    "Iterator": "collections.abc.Iterator",
    "Generator": "collections.abc.Generator",
    "Type": "type",
    "Pattern": "re.Pattern",
    "Match": "re.Match",
}

BARE_REPLACE = {
    "str": "str",
    "int": "int",
    "float": "float",
    "bool": "bool",
    "bytes": "bytes",
    "True": "True",
    "False": "False",
}

BARE_REGEXES = {
    re.compile(rf"(\[|, ]){k}(\]|, )"): v for k, v in {**CONTAINERS, **BARE_REPLACE}.items()
}
CONTAINER_REGEXES = {re.compile(rf"\b{k}\["): v for k, v in CONTAINERS.items()}

OPTIONAL = re.compile(r"Optional\[")
UNION = re.compile(r"Union\[")
ANY = re.compile(r"(\||, ?|\[)Any\b")
NONE = re.compile(r"``None``")


def get_check_sections(s: str) -> list[tuple[str, bool]]:
    """Return a list of (segment, should_replace) tuples for segments of s.

    Segments are parts of the string that are either inside or outside of quotes, or inside
    a code block directive.
    """
    parts = s.split("``")
    segments = []
    # parts alternate: outside, inside, outside, inside, ...
    for i, part in enumerate(parts):
        if i != len(parts) - 1:
            part += "``"
        if i % 2 == 1:
            # inside a double-backtick fenced span -> keep whole part and mark True
            segments.append((part, False))
            continue

        # outside a fenced span: inspect line-by-line to detect code-blocks
        lines = part.splitlines(keepends=True)
        in_code_block = False
        block_indent: int = 0

        for line in lines:
            if in_code_block:
                if line.strip() == "" or (block_indent and line.startswith(" " * block_indent)):
                    segments.append((line, False))
                    continue
                in_code_block = False
                block_indent = 0

            m = re.match(r"^([ \t]*)\.\.\s+code-block::.*\n?$", line)
            if m:
                in_code_block = True
                block_indent = len(m.group(1)) + 1
                segments.append((line, False))
                continue

            segments.append((line, True))

    if not segments:
        return []
    merged: list[tuple[str, bool]] = [segments[0]]
    for seg, flag in segments[1:]:
        prev_seg, prev_flag = merged[-1]
        if prev_flag == flag:
            merged[-1] = (prev_seg + seg, prev_flag)
        else:
            merged.append((seg, flag))
    return merged


def apply_replacements(s):
    # Replace Optional[A] with A | ``None`` using proper bracket matching
    def replace_all_optionals(text: str) -> str:
        while True:
            m = OPTIONAL.search(text)
            if not m:
                break
            start = m.end()
            bracket_count = 1
            for idx, ch in enumerate(text[start:], start=start):
                if ch == "[":
                    bracket_count += 1
                elif ch == "]":
                    bracket_count -= 1
                if bracket_count == 0:
                    inner = text[start:idx]
                    inner = replace_all_optionals(inner)
                    text = text[: m.start()] + inner + " | ``None``" + text[idx + 1 :]
                    break
            else:
                break
        return text

    def replace_all_unions(text: str) -> str:
        # Find each 'Union[' and replace it with the top-level elements joined by ' | '
        # while preserving nested brackets (do not split commas inside nested []).
        while True:
            m = UNION.search(text)
            if not m:
                break
            start = m.end()
            bracket_count = 1
            found = False
            for idx, ch in enumerate(text[start:], start=start):
                if ch == "[":
                    bracket_count += 1
                elif ch == "]":
                    bracket_count -= 1
                if bracket_count == 0:
                    inner = text[start:idx]
                    # Split inner on top-level commas only
                    parts = []
                    curr = []
                    depth = 0
                    for c in inner:
                        if c == "[":
                            depth += 1
                        elif c == "]":
                            depth -= 1
                        if c == "," and depth == 0:
                            parts.append("".join(curr).strip())
                            curr = []
                        else:
                            curr.append(c)
                    parts.append("".join(curr).strip())
                    new_inner = " | ".join(parts)
                    text = text[: m.start()] + new_inner + text[idx + 1 :]
                    found = True
                    break
            if not found:
                break
        return text

    # replace Union[...] occurrences
    s = replace_all_unions(s)

    s = replace_all_optionals(s)

    parts = get_check_sections(s)
    s = ""
    for part, should_check in parts:
        if should_check:
            for regex, replacement in BARE_REGEXES.items():
                part = regex.sub(rf"\1:class:`{replacement}`\2", part)

            for regex, replacement in CONTAINER_REGEXES.items():
                part = regex.sub(rf":class:`{replacement}`\\\\[", part)

            part = ANY.sub(r"\1:data:`~typing.Any`", part)
        s += part

    s = NONE.sub(r":data:`None`", s)

    return s


class DocstringTransformer(BaseCodemodCommand):
    DESCRIPTION = "Replace type hints in docstrings with PEP 585/604 style."

    def _replace_simple_string(self, simple_string: cst.SimpleString) -> cst.SimpleString:
        # simple_string.value is the literal including quotes and prefixes
        current = simple_string.raw_value
        prefix = simple_string.prefix

        new_inner = apply_replacements(current)
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
