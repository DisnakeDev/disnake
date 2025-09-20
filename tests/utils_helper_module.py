# SPDX-License-Identifier: MIT

"""Separate module file for some test_utils.py type annotation tests."""

import sys
from typing import TYPE_CHECKING, List, TypeVar, Union

version = sys.version_info  # assign to variable to trick pyright

if TYPE_CHECKING:
    from typing_extensions import TypeAliasType
elif version >= (3, 12):
    # non-3.12 tests shouldn't be using this
    from typing import TypeAliasType

if version >= (3, 12):
    CoolUniqueIntOrStrAlias = Union[int, str]
    ListWithForwardRefAlias = TypeAliasType(
        "ListWithForwardRefAlias", List["CoolUniqueIntOrStrAlias"]
    )

    T = TypeVar("T")
    GenericListAlias = TypeAliasType("GenericListAlias", List[T], type_params=(T,))

    DuplicateAlias = str
    ListWithDuplicateAlias = TypeAliasType("ListWithDuplicateAlias", List["DuplicateAlias"])
