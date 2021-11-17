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
import inspect
import itertools
import math
import warnings
from enum import Enum, EnumMeta
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    ForwardRef,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    get_origin,
)

import disnake
from disnake.app_commands import Option, OptionChoice
from disnake.channel import _channel_type_factory
from disnake.enums import ChannelType, OptionType, try_enum_to_int
from disnake.ext import commands
from disnake.interactions import ApplicationCommandInteraction as Interaction
from disnake.utils import maybe_coroutine

from . import errors
from .converter import CONVERTER_MAPPING

if TYPE_CHECKING:
    from .slash_core import InvokableSlashCommand, SubCommand

    AnySlashCommand = Union[InvokableSlashCommand, SubCommand]

    from typing_extensions import TypeGuard

T = TypeVar("T", bound=Any)
TypeT = TypeVar("TypeT", bound=Type[Any])
CallableT = TypeVar("CallableT", bound=Callable[..., Any])
ChoiceValue = Union[str, int, float]
Choices = Union[List[OptionChoice], List[ChoiceValue], Dict[str, ChoiceValue]]
TChoice = TypeVar("TChoice", bound=ChoiceValue)

__all__ = (
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


def evaluate_forwardref(annotation: Any, globalns: Dict[str, Any]) -> Any:
    if isinstance(annotation, (str, ForwardRef)):
        if isinstance(annotation, str):
            annotation = ForwardRef(annotation)

        try:
            annotation._evaluate(globalns, globalns, recursive_guard=frozenset())  # type: ignore
        except Exception as e:
            warnings.warn(f"Cannot parse annotation: {annotation!r}")

    return annotation


def signature(function: Callable) -> inspect.Signature:
    """Get the signature with evaluated annotations wherever possible"""
    globalns = function.__globals__
    sig = inspect.signature(function)
    parameters = []
    for parameter in sig.parameters.values():
        annotation = evaluate_forwardref(parameter.annotation, globalns)
        parameter = parameter.replace(annotation=annotation)

        # remove unwanted optionals
        if get_origin(parameter.annotation) is Union and parameter.default is not parameter.empty:
            parameter.annotation = cast(Any, parameter.annotation)

            args = [i for i in parameter.annotation.__args__ if i not in (None, type(None))]
            if len(args) == 1:
                parameter.annotation = args[0]
            else:
                parameter.annotation.__args__ = args

        parameters.append(parameter)

    return_annotation = evaluate_forwardref(sig.return_annotation, globalns)

    return inspect.Signature(parameters, return_annotation=return_annotation)


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


class ParamInfo:
    """
    A class that basically connects function params with slash command options.
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
    choices: Iterable[Any]
        The list of choices of this slash command option.
    ge: :class:`float`
        The lowest allowed value for this option.
    le: :class:`float`
        The greatest allowed value for this option.
    type: Any
        The type of the parameter.
    channel_types: List[:class:`ChannelType`]
        The list of channel types supported by this slash command option.
    autocomplete: Callable[[:class:`ApplicationCommandInteraction`, :class:`str`], Any]
        The function that will suggest possible autocomplete options while typing.
    converter: Callable[[:class:`ApplicationCommandInteraction`, Any], Any]
        The function that will convert the original input to a desired format.
    """

    TYPES: ClassVar[Dict[type, int]] = {
        str: 3,
        int: 4,
        bool: 5,
        disnake.abc.User: 6,
        disnake.User: 6,
        disnake.Member: 6,
        Union[disnake.User, disnake.Member]: 6,
        # channels handled separately
        disnake.abc.GuildChannel: 7,
        disnake.Role: 8,
        Union[disnake.Member, disnake.Role]: 9,
        disnake.abc.Snowflake: 9,
        float: 10,
    }
    _registered_converters: ClassVar[Dict[type, Callable]] = {}

    def __init__(
        self,
        default: Any = ...,
        *,
        name: str = "",
        description: str = None,
        converter: Callable[[Interaction, Any], Any] = None,
        autcomplete: Callable[[Interaction, str], Any] = None,
        choices: Choices = None,
        type: type = None,
        channel_types: List[ChannelType] = None,
        lt: float = None,
        le: float = None,
        gt: float = None,
        ge: float = None,
    ) -> None:
        self.default = default
        self.name = name
        self.param_name = name
        self.description = description
        self.converter = converter
        self.autocomplete = autcomplete
        self.choices = choices or []
        self.type = type or str
        self.channel_types = channel_types or []
        self.max_value = _xt_to_xe(le, lt, -1)
        self.min_value = _xt_to_xe(ge, gt, 1)

    @property
    def required(self) -> bool:
        return self.default is ...

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
        parsed_docstring: Dict[str, Any] = None,
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

    async def get_default(self, inter: Interaction) -> Any:
        """Gets the default for an interaction"""
        if not callable(self.default):
            return self.default

        default = self.default(inter)
        if inspect.isawaitable(default):
            return await default

        return default

    async def verify_type(self, inter: Interaction, argument: Any) -> Any:
        """Check if a type of an argument is correct and possibly fix it"""
        # these types never need to be verified
        if self.discord_type.value in [3, 4, 5, 8, 9, 10]:
            return argument

        if issubclass(self.type, disnake.Member):
            if isinstance(argument, disnake.Member):
                return argument

            raise errors.MemberNotFound(str(argument.id))

        if issubclass(self.type, disnake.abc.GuildChannel):
            if isinstance(argument, self.type):
                return argument

            raise errors.ChannelNotFound(str(argument.id))

        # unexpected types may just be ignored
        return argument

    async def convert_argument(self, inter: Interaction, argument: Any) -> Any:
        """Convert a value if a converter is given"""
        if self.converter is None:
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

    def _parse_guild_channel(self, *channels: Type[disnake.abc.GuildChannel]) -> None:
        self.type = disnake.abc.GuildChannel

        if not self.channel_types:
            channel_types = set()
            for channel in channels:
                channel_types.union(_channel_type_factory(channel))
            self.channel_types = list(channel_types)

    def parse_annotation(self, annotation: Any, converter_mode: bool = False) -> bool:
        """Parse an annotation"""
        if not converter_mode:
            self.converter = getattr(annotation, "__discord_converter__", None)
            self.converter = self.converter or self._registered_converters.get(annotation)
            if self.converter:
                self.parse_converter_annotation(self.converter, annotation)
                return True

        if annotation is inspect.Parameter.empty or annotation is Any:
            pass
        elif annotation in self.TYPES:
            self.type = annotation
        elif (
            isinstance(annotation, (EnumMeta, disnake.enums.EnumMeta))
            or get_origin(annotation) is Literal
        ):
            self._parse_enum(annotation)
        elif get_origin(annotation) is Union:
            args = annotation.__args__
            if all(issubclass_(channel, disnake.abc.GuildChannel) for channel in args):
                self._parse_guild_channel(*args)
            else:
                raise TypeError(
                    "Unions for anything else other than channels or a mentionable are not supported"
                )
        elif issubclass_(annotation, disnake.abc.GuildChannel):
            self._parse_guild_channel(annotation)

        elif not converter_mode and annotation in CONVERTER_MAPPING:
            self.converter = CONVERTER_MAPPING[annotation]().convert
        elif converter_mode:
            return False
        else:
            raise TypeError(f"{annotation!r} is not a valid Param annotation")

        return True

    def parse_converter_annotation(self, converter: Callable, fallback_annotation: Any) -> None:
        _, parameters = isolate_self(converter)

        if len(parameters) != 1:
            raise TypeError(
                "Converters must take precisely one argument (excluding self and an optional interaction)"
            )

        _, parameter = parameters.popitem()
        annotation = parameter.annotation

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
            description=self.description or "\u200b",
            type=self.discord_type,
            required=self.required,
            choices=self.choices or None,
            channel_types=self.channel_types,
            autocomplete=self.autocomplete is not None,
            min_value=self.min_value,
            max_value=self.max_value,
        )


def safe_call(function: Callable[..., T], *args: Any, **possible_kwargs: Any) -> T:
    """Calls a function without providing any extra unexpected arguments"""
    parsed_pos = False
    sig = signature(function)

    kwargs = {}

    for index, parameter, posarg in itertools.zip_longest(
        itertools.count(), sig.parameters.values(), args
    ):
        if parameter is None:
            if posarg is not None:
                args = args[:index]
                kwargs = {}
            break
        if posarg is None:
            parsed_pos = True
        if parsed_pos and parameter.name in possible_kwargs:
            kwargs[parameter.name] = possible_kwargs[parameter.name]

    return function(*args, **kwargs)


def isolate_self(
    function: Callable,
) -> Tuple[Tuple[Optional[inspect.Parameter], ...], Dict[str, inspect.Parameter]]:
    """Create parameters without self and the first interaction"""
    is_interaction = (
        lambda annot: issubclass_(annot, Interaction) or annot is inspect.Parameter.empty
    )

    sig = signature(function)

    parameters = dict(sig.parameters)
    parametersl = list(sig.parameters.values())

    if not parameters:
        return (None, None), {}

    self_param: Optional[inspect.Parameter] = None
    inter_param: Optional[inspect.Parameter] = None

    if parametersl[0].name == "self":
        self_param = parameters.pop(parametersl[0].name)
        parametersl.pop(0)
        if len(parameters) > 1 and is_interaction(parametersl[0].annotation):
            inter_param = parameters.pop(parametersl[0].name)
    if inter_param is None and is_interaction(parametersl[0].annotation):
        inter_param = parameters.pop(parametersl[0].name)

    return (self_param, inter_param), parameters


def collect_params(
    function: Callable,
) -> Tuple[Optional[str], Optional[str], List[ParamInfo], Dict[str, Injection]]:
    """Collect all parameters in a function

    Returns: (`self parameter`, `interaction parameter`, `param infos`, `injections`)
    """
    (self_param, inter_param), parameters = isolate_self(function)
    doc = disnake.utils.parse_docstring(function)

    if not parameters:
        return None, None, [], {}

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
        elif issubclass_(parameter.annotation, Interaction):
            if inter_param is None:
                inter_param = parameter
            else:
                raise TypeError(
                    f"Found two candidates for the interaction in {function!r}: {inter_param.name} and {parameter.name}"
                )
        else:
            paraminfo = ParamInfo.from_param(parameter, {}, doc)
            paraminfos.append(paraminfo)

    return (
        self_param.name if self_param else None,
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
    interaction: Interaction,
    self_param: str = None,
    inter_param: str = None,
    *args: Any,
    **kwargs: Any,
) -> Dict[str, Any]:
    cog: Optional[commands.Cog] = None

    for arg in args:
        if isinstance(arg, commands.Cog):
            cog = arg
        else:
            raise TypeError(f"Unexpected positional argument in a command callback: {arg}")

    if self_param:
        kwargs[self_param] = cog
    if inter_param:
        kwargs[inter_param] = interaction

    return kwargs


async def run_injections(
    injections: Dict[str, Injection], interaction: Interaction, *args: Any, **kwargs: Any
) -> Dict[str, Any]:
    """Run and resolve a list of injections"""

    async def _helper(name: str, injection: Injection) -> Tuple[str, Any]:
        return name, await call_param_func(injection.function, interaction, *args, **kwargs)

    resolved = await asyncio.gather(*(_helper(name, i) for name, i in injections.items()))
    return dict(resolved)


async def call_param_func(
    function: Callable, interaction: Interaction, *args: Any, **kwargs: Any
) -> Any:
    """Call a function utilizing ParamInfo"""
    self_param, inter_param, paraminfos, injections = collect_params(function)
    formatted_kwargs = format_kwargs(interaction, self_param, inter_param, *args, **kwargs)
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
    params = collect_nested_params(command.callback)

    # update connectors and autocompleters
    for param in params:
        if param.name != param.param_name:
            command.connectors[param.name] = param.param_name
        if param.autocomplete:
            command.autocompleters[param.name] = param.autocomplete

    # TODO: Apply stuff like GuildCommandInteraction

    return [param.to_option() for param in params]


def Param(
    default: Any = ...,
    *,
    name: str = "",
    description: str = None,
    choices: Choices = None,
    converter: Callable[[Interaction, Any], Any] = None,
    autocomplete: Callable[[Interaction, str], Any] = None,
    channel_types: List[ChannelType] = None,
    lt: float = None,
    le: float = None,
    gt: float = None,
    ge: float = None,
    **kwargs: Any,
) -> Any:
    """
    A special function that creates an instance of :class:`ParamInfo` that contains some information about a
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
    choices: Iterable[Any]
        A list of choices for this option.
    channel_types: Iterable[:class:`ChannelType`]
        A list of channel types that should be allowed.
        By default these are discerned from the annotation.
    min_value: :class:`float`
        The lowest allowed value for this option. Kwarg aliases: ``ge``, ``gt``.
    max_value: :class:`float`
        The greatest allowed value for this option. Kwarg aliases: ``le``, ``lt``.
    autocomplete: Callable[[:class:`ApplicationCommandInteraction`, :class:`str`], Any]
        A function that will suggest possible autocomplete options while typing.
        See :ref:`param_syntax`. Kwarg aliases: ``autocomp``.
    converter: Callable[[:class:`ApplicationCommandInteraction`, Any], Any]
        A function that will convert the original input to a desired format.
        Kwarg aliases: ``conv``.

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
        autcomplete=autocomplete,
        channel_types=channel_types,
        lt=lt,
        le=le,
        gt=gt,
        ge=ge,
    )


param = Param


def inject(function: Callable[..., Any]) -> Any:
    return Injection(function)


def option_enum(
    choices: Union[Dict[str, TChoice], List[TChoice]], **kwargs: TChoice
) -> Type[TChoice]:
    if isinstance(choices, list):
        # invariance issue, please fix
        choices = cast(Dict[str, TChoice], {str(i): i for i in choices})

    choices = choices or kwargs
    first, *_ = choices.values()
    return Enum("", choices, type=type(first))


class ConverterMethod:
    function: classmethod

    def __init__(self, function) -> None:
        if not isinstance(function, classmethod):
            function = classmethod(function)

        self.function = function

    def __set_name__(self, owner: Type[Any], name: str):
        ParamInfo._registered_converters[owner] = self.function
        owner.__discord_converter__ = self.function

    def __get__(self, instance: Any, cls: Any):
        return self.function


if TYPE_CHECKING:
    converter_method = classmethod
else:

    def converter_method(function: Any) -> ConverterMethod:
        return ConverterMethod(function)


def register_injection(function: CallableT) -> CallableT:
    """Use this as a decorator to register a global injection"""
    sig = signature(function)
    tp = sig.return_annotation

    if tp is inspect.Parameter.empty:
        raise TypeError("Injection must have a return annotation")
    if tp in ParamInfo.TYPES:
        raise TypeError("Injection cannot overwrite builtin types")

    Injection.register(function, sig.return_annotation)
    return function
