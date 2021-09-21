"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz, 2021-present EQUENOS

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from disnake.ext.commands.flags import Any, BadFlagArgument, CommandError, Dict, F, Flag, FlagConverter, FlagsMeta, Iterator, List, Literal, MISSING, MissingFlagArgument, MissingRequiredFlag, Optional, Pattern, Set, StringView, TYPE_CHECKING, TooManyFlags, Tuple, Type, TypeVar, Union, annotations, convert_flag, dataclass, field, flag, get_flags, inspect, maybe_coroutine, re, resolve_annotation, run_converters, sys, tuple_convert_all, tuple_convert_flag, validate_flag_name
__all__ = ('Flag', 'flag', 'FlagConverter')