# SPDX-License-Identifier: MIT
"""Update type hints in docs files to use pep 585 and pep 602 style."""

import re

CONTAINERS = {
    "Dict": "dict",
    "List": "list",
    "Set": "set",
    "Tuple": "tuple",
    "FrozenSet": "frozenset",
    "Sequence": "~collections.abc.Sequence",
    "Mapping": "~collections.abc.Mapping",
    "Callable": "~collections.abc.Callable",
    "Collection": "~collections.abc.Collection",
    "Coroutine": "~collections.abc.Coroutine",
    "AsyncGenerator": "~collections.abc.AsyncGenerator",
    "AsyncIterable": "~collections.abc.AsyncIterable",
    "Awaitable": "~collections.abc.Awaitable",
    "Iterable": "~collections.abc.Iterable",
    "Iterator": "~collections.abc.Iterator",
    "Generator": "~collections.abc.Generator",
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


def apply_replacements(s: str, *, include_double_backslash: bool = False) -> str:
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
                if include_double_backslash:
                    part = regex.sub(rf":class:`{replacement}`\\\\[", part)
                else:
                    part = regex.sub(rf":class:`{replacement}`\\[", part)

            part = ANY.sub(r"\1:data:`~typing.Any`", part)
        s += part

    return NONE.sub(r":data:`None`", s)


def process_file(file_path) -> None:
    with open(file_path, encoding="utf-8", newline="") as f:
        # Normalize line endings to LF for processing
        content = f.read().replace("\r\n", "\n")

    new_content = apply_replacements(content)
    # Ensure LF line endings
    new_content = new_content.replace("\r\n", "\n")
    with open(file_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_content)
