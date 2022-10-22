# SPDX-License-Identifier: MIT


"""Add all special cog methods to the full list contained in disnake.__main__.

This script does not run automatically and special methods that are removed from cogs
must also be removed from the list manually.
"""
from __future__ import annotations

import inspect
import os
import re
import sys
import textwrap
from typing import Dict, Union

_RE = r""" = ["']{3}\n(.+?)\n["']{3}"""


def remove_annotations_from_sig(sig: inspect.Signature) -> inspect.Signature:
    return sig.replace(
        parameters=[
            param.replace(annotation=inspect.Parameter.empty) for param in sig.parameters.values()
        ],
        return_annotation=inspect.Signature.empty,
    )


def get_cog_special_methods() -> Dict[str, str]:

    from disnake.ext.commands import Cog

    _sentinel = object()
    result: Dict[str, str] = {}
    for name, attr in sorted((name, getattr(Cog, name)) for name in dir(Cog)):
        if getattr(attr, "__cog_special_method__", _sentinel) is _sentinel:
            continue

        async_ = "async " if inspect.iscoroutinefunction(attr) else ""
        sig = inspect.signature(attr)
        sig = remove_annotations_from_sig(sig)
        result[name] = f"{async_}def {name}{str(sig)}:"

    return result


def format_sig(name: str, sig: str, body: str = "...") -> str:
    body = textwrap.indent(textwrap.dedent(body), " " * 4)
    return f"{sig}\n{body}\n"


def merge_methods(contents: str, methods: Dict[str, str]) -> str:

    for name, sig in methods.items():

        if f"def {name}" in contents:
            # check that the signature is the same
            missing_async = False
            if sig not in contents or (
                missing_async := (not sig.startswith("async") and ("async " + sig) in contents)
            ):
                # find the current sig
                missing_async = "async " if missing_async else ""

                current_sig = re.search(rf"{missing_async}def {re.escape(name)}.+?\n", contents)
                if current_sig:
                    current_sig = current_sig.string[current_sig.start() : current_sig.end()]
                raise RuntimeError(
                    f"the signature for method '{name}' is different from what already exists.\n"
                    f"Current sig: {current_sig}\n"
                    f"Expected sig: {sig}"
                )
            continue

        sig = format_sig(name, sig)
        contents = "".join((contents, "\n", sig))

    return contents


def update_file(file: Union[str, os.PathLike], attr: str, methods: Dict[str, str]) -> bool:
    regex = re.compile(str(re.escape(attr)) + _RE, flags=re.S)
    with open(file, "r") as f:
        contents = f.read()

    match = regex.search(contents)

    if not match:
        raise RuntimeError(f"could not find the {attr} definition in {file}.")
    var_contents = match.group(1)
    var_contents = textwrap.dedent(var_contents)
    var_contents = merge_methods(var_contents, methods).strip()
    var_contents = textwrap.indent(var_contents, " " * 4)

    # replace the regex
    new_var = f'{attr} = """\n{var_contents}\n\n"""'
    contents = regex.sub(new_var, contents)

    with open(file, "w") as f:
        f.write(contents)

    return True


def main() -> int:
    ...
    methods = get_cog_special_methods()

    return update_file("disnake/__main__.py", "_cog_extras", methods)


if __name__ == "__main__":
    sys.exit(main())
