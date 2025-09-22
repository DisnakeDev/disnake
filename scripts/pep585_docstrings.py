"""Update docstrings to use pep 585 and pep 602 style type hints for documentation."""

# SPDX-License-Identifier: MIT

import pathlib
import re
import sys


def apply_replacements(s):
    # Replace Optional[A] with A | ``None`` using proper bracket matching
    def replace_optional(match):
        content = match.group()
        start_pos = 9
        bracket_count = 1
        for i, char in enumerate(content[start_pos:], start=start_pos):
            if char == "[":
                bracket_count += 1
            elif char == "]":
                bracket_count -= 1
            if bracket_count == 0:
                inner_content = content[start_pos:i]  # Content between Optional[ and matching ]
                inner_content = re.sub(r"Optional\[.*?\]", replace_optional, inner_content)
                return inner_content + " | ``None``"
        # Fallback if no matching bracket found
        return content

    s = re.sub(
        r"Union\[([^]]+)\]",
        lambda m: " | ".join([x.strip() for x in m.group(1).split(",")]),
        s,
    )
    s = re.sub(r"Optional\[.*\]", replace_optional, s)

    containers = {
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
    for type_name, replacement in containers.items():
        s = re.sub(rf"\b{type_name}\[", rf":class:`{replacement}`\\\\[", s)

    s = re.sub(r"(\||, ?|\[)Any\b", r"\1:class:`~typing.Any`", s)
    # # reference to all None's
    s = re.sub(r"``None``", r":obj:`None`", s)

    return s


def process_file(file_path) -> None:
    with open(file_path, "rb") as f:
        content = f.read().decode("utf-8")

    def replace_in_docstring(match):
        s = match.group(1)
        return '"""' + apply_replacements(s) + '"""'

    new_content = re.sub(r'"""(.*?)"""', replace_in_docstring, content, flags=re.DOTALL)
    # Ensure LF line endings
    new_content = new_content.replace("\r\n", "\n")
    with open(file_path, "wb") as f:
        f.write(new_content.encode("utf-8"))


if __name__ == "__main__":
    if sys.argv[1:]:
        paths = [pathlib.Path(p) for p in sys.argv[1:]]
    else:
        paths = [pathlib.Path("disnake")]
    for path in paths:
        for file_path in path.glob("**/*.py"):
            process_file(file_path)
