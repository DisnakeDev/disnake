# The MIT License (MIT)

# Copyright (c) 2021-present EQUENOS

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

"""Repsonsible for handling Params for slash commands"""
from __future__ import annotations

import asyncio
import collections.abc
import inspect
import itertools
import math
import sys
from enum import Enum, EnumMeta
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    get_origin,
    get_type_hints,
    overload,
)

import disnake
from disnake.app_commands import Option, OptionChoice
from disnake.channel import _channel_type_factory
from disnake.enums import ChannelType, OptionType, try_enum_to_int
from disnake.ext import commands
from disnake.interactions import CommandInteraction
from disnake.utils import maybe_coroutine

from . import errors
from .converter import CONVERTER_MAPPING

if TYPE_CHECKING:
    from disnake.app_commands import Choices
    from disnake.types.interactions import ApplicationCommandOptionChoiceValue

    from .slash_core import InvokableSlashCommand, SubCommand

    AnySlashCommand = Union[InvokableSlashCommand, SubCommand]

    from typing_extensions import TypeGuard

    TChoice = TypeVar("TChoice", bound=ApplicationCommandOptionChoiceValue)

if sys.version_info >= (3, 10):
    from types import UnionType
else:
    UnionType = object()

T = TypeVar("T", bound=Any)
TypeT = TypeVar("TypeT", bound=Type[Any])
CallableT = TypeVar("CallableT", bound=Callable[..., Any])

__all__ = (
    "Range",
    "LargeInt",
    "ParamInfo",
    "Param",
    "param",
    "inject",
    "option_enum",
    "register_injection",
    "converter_method",
)


def issubclass_(obj: Any, tp: Union[TypeT, Tuple[TypeT, ...]]) -> TypeGuard[TypeT]:
    if not isinstance(obj, type) or not isinstance(tp, (type, tuple)):
        return False
    return issubclass(obj, tp)


def remove_optionals(annotation: Any) -> Any:
    """remove unwanted optionals from an annotation"""
    if get_origin(annotation) in (Union, UnionType):
        annotation = cast(Any, annotation)

        args = tuple(i for i in annotation.__args__ if i not in (None, type(None)))
        if len(args) == 1:
            annotation = args[0]
        else:
            annotation = Union[args]  # type: ignore

    return annotation


def signature(func: Callable) -> inspect.Signature:
    """Get the signature with evaluated annotations wherever possible

    This is equivalent to `signature(..., eval_str=True)` in python 3.10
    """
    if sys.version_info >= (3, 10):
        return inspect.signature(func, eval_str=True)

    if inspect.isfunction(func) or inspect.ismethod(func):
        typehints = get_type_hints(func)
    else:
        typehints = get_type_hints(func.__call__)

    signature = inspect.signature(func)
    parameters = []

    for name, param in signature.parameters.items():
        if isinstance(param.annotation, str):
            param = param.replace(annotation=typehints.get(name, inspect.Parameter.empty))
        if param.annotation is type(None):
            param = param.replace(annotation=None)

        parameters.append(param)

    return_annotation = typehints.get("return", inspect.Parameter.empty)
    if return_annotation is type(None):
        return_annotation = None

    return signature.replace(parameters=parameters, return_annotation=return_annotation)


def _xt_to_xe(xe: Optional[float], xt: Optional[float], direction: float = 1) -> Optional[float]:
    """Function for combining xt and xe

    * x > xt && x >= xe ; x >= f(xt, xe, 1)
    * x < xt && x <= xe ; x <= f(xt, xe, -1)
    """
    if xe is not None:
        if xt is not None:
            raise TypeError("Cannot combine lt and le or gt and le")
        return xe
    elif xt is not None:
        epsilon = math.ldexp(1.0, -1024)
        return xt + (epsilon * direction)
    else:
        return None


class Injection:
    _registered: ClassVar[Dict[Any, Injection]] = {}

    function: Callable

    def __init__(self, function: Callable) -> None:
        self.function = function

    @classmethod
    def register(cls, function: CallableT, annotation: Any) -> CallableT:
        self = cls(function)
        cls._registered[annotation] = self
        return function


class RangeMeta(type):
    """Custom Generic implementation for Range"""

    @overload
    def __getitem__(self, args: Tuple[Union[int, ellipsis], Union[int, ellipsis]]) -> Type[int]:
        ...

    @overload
    def __getitem__(
        self, args: Tuple[Union[float, ellipsis], Union[float, ellipsis]]
    ) -> Type[float]:
        ...

    def __getitem__(self, args: Tuple[Any, ...]) -> Any:
        a, b = [None if x is Ellipsis else x for x in args]
        return Range.create(min_value=a, max_value=b)


class Range(type, metaclass=RangeMeta):
    """Type depicting a limited range of allowed values"""

    min_value: Optional[float]
    max_value: Optional[float]

    @overload
    @classmethod
    def create(
        cls,
        min_value: int = None,
        max_value: int = None,
        *,
        le: int = None,
        lt: int = None,
        ge: int = None,
        gt: int = None,
    ) -> Type[int]:
        ...

    @overload
    @classmethod
    def create(
        cls,
        min_value: float = None,
        max_value: float = None,
        *,
        le: float = None,
        lt: float = None,
        ge: float = None,
        gt: float = None,
    ) -> Type[float]:
        ...

    @classmethod
    def create(
        cls,
        min_value: float = None,
        max_value: float = None,
        *,
        le: float = None,
        lt: float = None,
        ge: float = None,
        gt: float = None,
    ) -> Any:
        """Construct a new range with any possible constraints"""
        self = cls(cls.__name__, (), {})
        self.min_value = min_value if min_value is not None else _xt_to_xe(le, lt, -1)
        self.max_value = max_value if max_value is not None else _xt_to_xe(ge, gt, 1)
        return self

    @property
    def underlying_type(self) -> Union[Type[int], Type[float]]:
        if isinstance(self.min_value, float) or isinstance(self.max_value, float):
            return float

        return int

    def __repr__(self) -> str:
        a = "..." if self.min_value is None else self.min_value
        b = "..." if self.max_value is None else self.max_value
        return f"{type(self).__name__}[{a}, {b}]"


class LargeInt(int):
    """Type for large integers in slash commands."""


class ParamInfo:
    """A class that basically connects function params with slash command options.
    The instances of this class are not created manually, but via the functional interface instead.
    See :func:`Param`.

    Attributes
    ----------
    default: Any
        The actual default value for the corresponding function param.
    name: :class:`str`
        The name of this slash command option.
    description: :class:`str`
        The description of this slash command option.
    choices: Union[List[:class:`.OptionChoice`], List[Union[:class:`str`, :class:`int`]], Dict[:class:`str`, Union[:class:`str`, :class:`int`]]]
        The list of choices of this slash command option.
    ge: :class:`float`
        The lowest allowed value for this option.
    le: :class:`float`
        The greatest allowed value for this option.
    type: Any
        The type of the parameter.
    channel_types: List[:class:`.ChannelType`]
        The list of channel types supported by this slash command option.
    autocomplete: Callable[[:class:`.ApplicationCommandInteraction`, :class:`str`], Any]
        The function that will suggest possible autocomplete options while typing.
    converter: Callable[[:class:`.ApplicationCommandInteraction`, Any], Any]
        The function that will convert the original input to a desired format.
    """

    TYPES: ClassVar[Dict[type, int]] = {
        # fmt: off
        str:                                 OptionType.string.value,
        int:                                 OptionType.integer.value,
        bool:                                OptionType.boolean.value,
        disnake.abc.User:                    OptionType.user.value,
        disnake.User:                        OptionType.user.value,
        disnake.Member:                      OptionType.user.value,
        Union[disnake.User, disnake.Member]: OptionType.user.value,
        # channels handled separately
        disnake.abc.GuildChannel:            OptionType.channel.value,
        disnake.Role:                        OptionType.role.value,
        Union[disnake.Member, disnake.Role]: OptionType.mentionable.value,
        disnake.abc.Snowflake:               OptionType.mentionable.value,
        float:                               OptionType.number.value,
        disnake.Attachment:                  OptionType.attachment.value,
        # fmt: on
    }
    _registered_converters: ClassVar[Dict[type, Callable]] = {}

    def __init__(
        self,
        default: Any = ...,
        *,
        name: str = "",
        description: str = None,
        converter: Callable[[CommandInteraction, Any], Any] = None,
        convert_default: bool = False,
        autcomplete: Callable[[CommandInteraction, str], Any] = None,
        choices: Choices = None,
        type: type = None,
        channel_types: List[ChannelType] = None,
        lt: float = None,
        le: float = None,
        gt: float = None,
        ge: float = None,
        large: bool = False,
    ) -> None:
        self.default = default
        self.name = name
        self.param_name = name
        self.description = description
        self.converter = converter
        self.convert_default = convert_default
        self.autocomplete = autcomplete
        self.choices = choices or []
        self.type = type or str
        self.channel_types = channel_types or []
        self.max_value = _xt_to_xe(le, lt, -1)
        self.min_value = _xt_to_xe(ge, gt, 1)
        self.large = large

    @property
    def required(self) -> bool:
        return self.default is Ellipsis

    @property
    def discord_type(self) -> OptionType:
        return OptionType(self.TYPES.get(self.type, OptionType.string.value))

    @discord_type.setter
    def discord_type(self, discord_type: OptionType) -> None:
        value = try_enum_to_int(discord_type)
        for t, v in self.TYPES.items():
            if value == v:
                self.type = t
                return

        raise TypeError(f"Type {discord_type} is not a valid Param type")

    @classmethod
    def from_param(
        cls,
        param: inspect.Parameter,
        type_hints: Dict[str, Any],
        parsed_docstring: Dict[str, disnake.utils._DocstringParam] = None,
    ) -> ParamInfo:
        # hopefully repeated parsing won't cause any problems
        parsed_docstring = parsed_docstring or {}

        if isinstance(param.default, cls):
            self = param.default
        else:
            default = param.default if param.default is not inspect.Parameter.empty else ...
            self = cls(default)

        self.parse_parameter(param)
        doc = parsed_docstring.get(param.name)
        if doc:
            self.parse_doc(doc["type"], doc["description"])
        self.parse_annotation(type_hints.get(param.name, param.annotation))

        return self

    @classmethod
    def register_converter(cls, annotation: Any, converter: CallableT) -> CallableT:
        cls._registered_converters[annotation] = converter
        return converter

    def __repr__(self) -> str:
        args = ", ".join(f"{k}={'...' if v is ... else repr(v)}" for k, v in vars(self).items())
        return f"{type(self).__name__}({args})"

    async def get_default(self, inter: CommandInteraction) -> Any:
        """Gets the default for an interaction"""
        default = self.default
        if callable(self.default):
            default = self.default(inter)

            if inspect.isawaitable(default):
                default = await default

        if self.convert_default:
            default = await self.convert_argument(inter, default)

        return default

    async def verify_type(self, inter: CommandInteraction, argument: Any) -> Any:
        """Check if a type of an argument is correct and possibly fix it"""
        if issubclass_(self.type, disnake.Member):
            if isinstance(argument, disnake.Member):
                return argument

            raise errors.MemberNotFound(str(argument.id))

        # unexpected types may just be ignored
        return argument

    async def convert_argument(self, inter: CommandInteraction, argument: Any) -> Any:
        """Convert a value if a converter is given"""
        if self.large:
            try:
                argument = int(argument)
            except Exception as e:
                raise errors.ConversionError(int, e) from e

        if self.converter is None:
            # TODO: Custom validators
            return await self.verify_type(inter, argument)

        try:
            argument = self.converter(inter, argument)
            if inspect.isawaitable(argument):
                return await argument

            return argument
        except Exception as e:
            raise errors.ConversionError(self.converter, e) from e

    def _parse_enum(self, annotation: Any) -> None:
        if isinstance(annotation, (EnumMeta, disnake.enums.EnumMeta)):
            self.choices = [OptionChoice(name, value.value) for name, value in annotation.__members__.items()]  # type: ignore
        else:
            self.choices = [OptionChoice(str(i), i) for i in annotation.__args__]

        self.type = type(self.choices[0].value)

    def _parse_guild_channel(
        self, *channels: Union[Type[disnake.abc.GuildChannel], Type[disnake.Thread]]
    ) -> None:
        # this variable continues to be GuildChannel because the type is still
        # determined from the TYPE mapping in the class definition
        self.type = disnake.abc.GuildChannel

        if not self.channel_types:
            channel_types = set()
            for channel in channels:
                channel_types.update(_channel_type_factory(channel))
            self.channel_types = list(channel_types)

    def parse_annotation(self, annotation: Any, converter_mode: bool = False) -> bool:
        """Parse an annotation"""
        annotation = remove_optionals(annotation)

        if not converter_mode:
            self.converter = (
                self.converter
                or getattr(annotation, "__discord_converter__", None)
                or self._registered_converters.get(annotation)
            )
            if self.converter:
                self.parse_converter_annotation(self.converter, annotation)
                return True

        # short circuit if user forgot to provide annotations
        if annotation is inspect.Parameter.empty or annotation is Any:
            return False

        # resolve type aliases
        if isinstance(annotation, Range):
            self.min_value = annotation.min_value
            self.max_value = annotation.max_value
            annotation = annotation.underlying_type
        if issubclass_(annotation, LargeInt):
            self.large = True
            annotation = int

        if self.large:
            self.type = str
            if annotation is not int:
                raise TypeError("Large integers must be annotated with int or LargeInt")
        elif annotation in self.TYPES:
            self.type = annotation
        elif (
            isinstance(annotation, (EnumMeta, disnake.enums.EnumMeta))
            or get_origin(annotation) is Literal
        ):
            self._parse_enum(annotation)
        elif get_origin(annotation) in (Union, UnionType):
            args = annotation.__args__
            if all(
                issubclass_(channel, (disnake.abc.GuildChannel, disnake.Thread)) for channel in args
            ):
                self._parse_guild_channel(*args)
            else:
                raise TypeError(
                    "Unions for anything else other than channels or a mentionable are not supported"
                )
        elif issubclass_(annotation, (disnake.abc.GuildChannel, disnake.Thread)):
            self._parse_guild_channel(annotation)
        elif issubclass_(get_origin(annotation), collections.abc.Sequence):
            raise TypeError(
                f"List arguments have not been implemented yet and therefore {annotation!r} is invalid"
            )

        elif annotation in CONVERTER_MAPPING:
            if converter_mode:
                raise TypeError(
                    f"{annotation!r} implies the usage of a converter but those cannot be nested"
                )
            self.converter = CONVERTER_MAPPING[annotation]().convert
        elif converter_mode:
            raise TypeError(f"{annotation!r} is not a valid converter annotation")
        else:
            raise TypeError(f"{annotation!r} is not a valid parameter annotation")

        return True

    def parse_converter_annotation(self, converter: Callable, fallback_annotation: Any) -> None:
        _, parameters = isolate_self(converter)

        if len(parameters) != 1:
            raise TypeError(
                "Converters must take precisely two arguments: the interaction and the argument"
            )

        _, parameter = parameters.popitem()
        annotation = parameter.annotation

        if parameter.default is not inspect.Parameter.empty and self.required:
            self.default = parameter.default
            self.convert_default = True

        success = self.parse_annotation(annotation, converter_mode=True)
        if success:
            return
        success = self.parse_annotation(fallback_annotation, converter_mode=True)
        if success:
            return

        raise TypeError(
            f"Both the converter annotation {annotation!r} and the option annotation {fallback_annotation!r} are invalid"
        )

    def parse_parameter(self, param: inspect.Parameter) -> None:
        self.name = self.name or param.name
        self.param_name = param.name

    def parse_doc(self, doc_type: Any, doc_description: str) -> None:
        self.description = self.description or doc_description
        if self.type == str and doc_type is not None:
            self.parse_annotation(doc_type)

    def to_option(self) -> Option:
        if self.name == "":
            raise TypeError("Param must be parsed first")

        return Option(
            name=self.name,
            description=self.description or "-",
            type=self.discord_type,
            required=self.required,
            choices=self.choices or None,
            channel_types=self.channel_types,
            autocomplete=self.autocomplete is not None,
            min_value=self.min_value,
            max_value=self.max_value,
        )


def safe_call(function: Callable[..., T], *possible_args: Any, **possible_kwargs: Any) -> T:
    """Calls a function without providing any extra unexpected arguments"""
    MISSING = object()
    sig = signature(function)

    kinds = {p.kind for p in sig.parameters.values()}
    arb = {inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD}
    if arb.issubset(kinds):
        raise TypeError(
            "Cannot safely call a function with both *args and **kwargs. "
            "If this is a wrapper please use functools.wraps to keep the signature correct"
        )

    parsed_pos = False
    args: List[Any] = []
    kwargs: Dict[str, Any] = {}

    for index, parameter, posarg in itertools.zip_longest(
        itertools.count(),
        sig.parameters.values(),
        possible_args,
        fillvalue=MISSING,
    ):
        if parameter is MISSING:
            break
        if posarg is MISSING:
            parsed_pos = True

        if parameter.kind is inspect.Parameter.VAR_POSITIONAL:
            args = list(possible_args)
            parsed_pos = True
        elif parameter.kind is inspect.Parameter.VAR_KEYWORD:
            kwargs = possible_kwargs
            break
        elif parameter.kind is inspect.Parameter.KEYWORD_ONLY:
            parsed_pos = True

        if not parsed_pos:
            args.append(possible_args[index])
        elif parameter.kind is inspect.Parameter.POSITIONAL_ONLY:
            break  # guaranteed error since not enough positional arguments
        elif parameter.name in possible_kwargs:
            kwargs[parameter.name] = possible_kwargs[parameter.name]

    return function(*args, **kwargs)


def isolate_self(
    function: Callable,
) -> Tuple[Tuple[Optional[inspect.Parameter], ...], Dict[str, inspect.Parameter]]:
    """Create parameters without self and the first interaction"""
    is_interaction = (
        lambda annot: issubclass_(annot, CommandInteraction) or annot is inspect.Parameter.empty
    )

    sig = signature(function)

    parameters = dict(sig.parameters)
    parametersl = list(sig.parameters.values())

    if not parameters:
        return (None, None), {}

    cog_param: Optional[inspect.Parameter] = None
    inter_param: Optional[inspect.Parameter] = None

    if parametersl[0].name == "self":
        cog_param = parameters.pop(parametersl[0].name)
        parametersl.pop(0)
    if parametersl and is_interaction(parametersl[0].annotation):
        inter_param = parameters.pop(parametersl[0].name)

    return (cog_param, inter_param), parameters


def collect_params(
    function: Callable,
) -> Tuple[Optional[str], Optional[str], List[ParamInfo], Dict[str, Injection]]:
    """Collect all parameters in a function

    Returns: (`cog parameter`, `interaction parameter`, `param infos`, `injections`)
    """
    (cog_param, inter_param), parameters = isolate_self(function)
    doc = disnake.utils.parse_docstring(function)["params"]

    paraminfos: List[ParamInfo] = []
    injections: Dict[str, Injection] = {}

    for parameter in parameters.values():
        if parameter.kind in [parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD]:
            continue
        if parameter.kind is parameter.POSITIONAL_ONLY:
            raise TypeError("Positional-only parameters cannot be used in commands")

        default = parameter.default
        if isinstance(default, Injection):
            injections[parameter.name] = default
        elif parameter.annotation in Injection._registered:
            injections[parameter.name] = Injection._registered[parameter.annotation]
        elif issubclass_(parameter.annotation, CommandInteraction):
            if inter_param is None:
                inter_param = parameter
            else:
                raise TypeError(
                    f"Found two candidates for the interaction parameter in {function!r}: {inter_param.name} and {parameter.name}"
                )
        elif issubclass_(parameter.annotation, commands.Cog):
            if cog_param is None:
                cog_param = parameter
            else:
                raise TypeError(
                    f"Found two candidates for the cog parameter in {function!r}: {cog_param.name} and {parameter.name}"
                )
        else:
            paraminfo = ParamInfo.from_param(parameter, {}, doc)
            paraminfos.append(paraminfo)

    return (
        cog_param.name if cog_param else None,
        inter_param.name if inter_param else None,
        paraminfos,
        injections,
    )


def collect_nested_params(function: Callable) -> List[ParamInfo]:
    """Collect all options from a function"""
    # TODO: Have these be actually sorted properly and not have injections always at the end

    _, _, paraminfos, injections = collect_params(function)

    for injection in injections.values():
        paraminfos += collect_nested_params(injection.function)

    return sorted(paraminfos, key=lambda param: not param.required)


def format_kwargs(
    interaction: CommandInteraction,
    cog_param: str = None,
    inter_param: str = None,
    *args: Any,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Create kwargs from appropriate information"""
    first = args[0] if args else None

    if len(args) > 1:
        raise TypeError(
            "When calling a slash command only self and the interaction should be positional"
        )
    elif first and not isinstance(first, commands.Cog):
        raise TypeError("Method slash commands may be created only in cog subclasses")

    cog: Optional[commands.Cog] = first

    if cog_param:
        kwargs[cog_param] = cog
    if inter_param:
        kwargs[inter_param] = interaction

    return kwargs


async def run_injections(
    injections: Dict[str, Injection], interaction: CommandInteraction, *args: Any, **kwargs: Any
) -> Dict[str, Any]:
    """Run and resolve a list of injections"""

    async def _helper(name: str, injection: Injection) -> Tuple[str, Any]:
        return name, await call_param_func(injection.function, interaction, *args, **kwargs)

    resolved = await asyncio.gather(*(_helper(name, i) for name, i in injections.items()))
    return dict(resolved)


async def call_param_func(
    function: Callable, interaction: CommandInteraction, *args: Any, **kwargs: Any
) -> Any:
    """Call a function utilizing ParamInfo"""
    cog_param, inter_param, paraminfos, injections = collect_params(function)
    formatted_kwargs = format_kwargs(interaction, cog_param, inter_param, *args, **kwargs)
    formatted_kwargs.update(await run_injections(injections, interaction, *args, **kwargs))
    kwargs = formatted_kwargs

    for param in paraminfos:
        if param.param_name in kwargs:
            kwargs[param.param_name] = await param.convert_argument(
                interaction, kwargs[param.param_name]
            )
        elif param.default is not ...:
            kwargs[param.param_name] = await param.get_default(interaction)

    return await maybe_coroutine(safe_call, function, **kwargs)


def expand_params(command: AnySlashCommand) -> List[Option]:
    """Update an option with its params *in-place*

    Returns the created options
    """
    sig = signature(command.callback)
    _, inter_param, params, injections = collect_params(command.callback)

    if inter_param is None:
        raise TypeError(f"Couldn't find an interaction parameter in {command.callback}")

    for injection in injections.values():
        params += collect_nested_params(injection.function)

    params = sorted(params, key=lambda param: not param.required)

    # update connectors and autocompleters
    for param in params:
        if param.name != param.param_name:
            command.connectors[param.name] = param.param_name
        if param.autocomplete:
            command.autocompleters[param.name] = param.autocomplete

    if issubclass_(sig.parameters[inter_param].annotation, disnake.GuildCommandInteraction):
        command.guild_only = True

    return [param.to_option() for param in params]


def Param(
    default: Any = ...,
    *,
    name: str = "",
    description: str = None,
    choices: Choices = None,
    converter: Callable[[CommandInteraction, Any], Any] = None,
    convert_defaults: bool = False,
    autocomplete: Callable[[CommandInteraction, str], Any] = None,
    channel_types: List[ChannelType] = None,
    lt: float = None,
    le: float = None,
    gt: float = None,
    ge: float = None,
    large: bool = False,
    **kwargs: Any,
) -> Any:
    """A special function that creates an instance of :class:`ParamInfo` that contains some information about a
    slash command option. This instance should be assigned to a parameter of a function representing your slash command.

    See :ref:`param_syntax` for more info.

    Parameters
    ----------
    default: Any
        The actual default value of the function parameter that should be passed instead of the :class:`ParamInfo` instance.
    name: :class:`str`
        The name of the option. By default, the option name is the parameter name.
    description: :class:`str`
        The description of the option. You can skip this kwarg and use docstrings. See :ref:`param_syntax`.
        Kwarg aliases: ``desc``.
    choices: Union[List[:class:`.OptionChoice`], List[Union[:class:`str`, :class:`int`]], Dict[:class:`str`, Union[:class:`str`, :class:`int`]]]
        A list of choices for this option.
    converter: Callable[[:class:`.ApplicationCommandInteraction`, Any], Any]
        A function that will convert the original input to a desired format.
        Kwarg aliases: ``conv``.
    convert_defaults: :class:`bool`
        Whether to also apply the converter to the provided default value.
        Defaults to ``False``.

        .. versionadded: 2.3
    autocomplete: Callable[[:class:`.ApplicationCommandInteraction`, :class:`str`], Any]
        A function that will suggest possible autocomplete options while typing.
        See :ref:`param_syntax`. Kwarg aliases: ``autocomp``.
    channel_types: Iterable[:class:`.ChannelType`]
        A list of channel types that should be allowed.
        By default these are discerned from the annotation.
    lt: :class:`float`
        The (exclusive) upper bound of values for this option (less-than).
    le: :class:`float`
        The (inclusive) upper bound of values for this option (less-than-or-equal). Kwarg aliases: ``max_value``.
    gt: :class:`float`
        The (exclusive) lower bound of values for this option (greater-than).
    ge: :class:`float`
        The (inclusive) lower bound of values for this option (greater-than-or-equal). Kwarg aliases: ``min_value``.
    large: :class:`bool`
        Whether to accept large :class:`int` values (if this is ``False``, only
        values in the range ``(-2^53, 2^53)`` would be accepted due to an API limitation).

        .. versionadded: 2.3

    Raises
    ------
    TypeError
        Unexpected keyword arguments were provided.

    Returns
    -------
    :class:`ParamInfo`
        An instance with the option info.
    """
    description = kwargs.pop("desc", description)
    converter = kwargs.pop("conv", converter)
    autocomplete = kwargs.pop("autocomp", autocomplete)
    le = kwargs.pop("max_value", le)
    ge = kwargs.pop("min_value", ge)

    if kwargs:
        a = ", ".join(map(repr, kwargs))
        raise TypeError(f"Param() got unexpected keyword arguments: {a}")

    return ParamInfo(
        default,
        name=name,
        description=description,
        choices=choices,
        converter=converter,
        convert_default=convert_defaults,
        autcomplete=autocomplete,
        channel_types=channel_types,
        lt=lt,
        le=le,
        gt=gt,
        ge=ge,
        large=large,
    )


param = Param


def inject(function: Callable[..., Any]) -> Any:
    """A special function to use the provided function for injections.
    This should be assigned to a parameter of a function representing your slash command.

    .. versionadded:: 2.3
    """
    return Injection(function)


def option_enum(
    choices: Union[Dict[str, TChoice], List[TChoice]], **kwargs: TChoice
) -> Type[TChoice]:
    if isinstance(choices, list):
        choices = {str(i): i for i in choices}

    choices = choices or kwargs
    first, *_ = choices.values()
    return Enum("", choices, type=type(first))


class ConverterMethod(classmethod):
    """A class to help register a method as a converter method."""

    def __set_name__(self, owner: Any, name: str):
        # this feels wrong
        function = self.__get__(None, owner)
        ParamInfo._registered_converters[owner] = function
        owner.__discord_converter__ = function


# due to a bug in pylance classmethod subclasses do not actually work properly
if TYPE_CHECKING:
    converter_method = classmethod
else:

    def converter_method(function: Any) -> ConverterMethod:
        """A decorator to register a method as the converter method.

        .. versionadded:: 2.3
        """
        return ConverterMethod(function)


def register_injection(function: CallableT) -> CallableT:
    """A decorator to register a global injection.

    .. versionadded:: 2.3
    """
    sig = signature(function)
    tp = sig.return_annotation

    if tp is inspect.Parameter.empty:
        raise TypeError("Injection must have a return annotation")
    if tp in ParamInfo.TYPES:
        raise TypeError("Injection cannot overwrite builtin types")

    Injection.register(function, sig.return_annotation)
    return function
