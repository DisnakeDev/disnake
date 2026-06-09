# SPDX-License-Identifier: MIT

import pytest

from disnake.ext.commands import FlagConverter

flag_def = """
class SomeFlags(FlagConverter):
    thing: str
    stuff_with_default: int = 1
"""


@pytest.mark.parametrize("with_future", [False, True])
def test_flags_annotations(with_future: bool) -> None:
    import __future__

    code_flags = __future__.annotations.compiler_flag if with_future else 0
    code = compile(flag_def, "", "exec", code_flags)
    exec(code, ns := {"FlagConverter": FlagConverter})  # noqa: S102

    SomeFlags: type[FlagConverter] = ns["SomeFlags"]
    flags = SomeFlags.get_flags()

    assert flags.keys() == {"thing", "stuff_with_default"}
    assert flags["thing"].annotation is str
    assert flags["stuff_with_default"].annotation is int
