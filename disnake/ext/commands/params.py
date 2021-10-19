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

import inspect
import math
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
from disnake.enums import OptionType, try_enum_to_int

from . import errors
from .converter import CONVERTER_MAPPING

if TYPE_CHECKING:
    from disnake.interactions import ApplicationCommandInteraction as Interaction

    from .slash_core import InvokableSlashCommand, SubCommand

    AnySlashCommand = Union[InvokableSlashCommand, SubCommand]

T = TypeVar("T", bound=Any)
ChoiceValue = Union[str, int, float]
Choices = Union[List[OptionChoice], List[ChoiceValue], Dict[str, ChoiceValue]]
TChoice = TypeVar("TChoice", bound=ChoiceValue)

__all__ = (
    "ParamInfo",
    "Param",
    "param",
    "option_enum",
)


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


class ParamInfo:
    """
    Parameters
    ----------
    default: Union[:class:`str`, Callable[[:class:`ApplicationCommandInteraction`, Any], Any]]
        default value or a default value factory
    name: :class:`str`
        option's name, the parameter name by default
    description: :class:`str`
        option's description
    converter: Callable[[:class:`ApplicationCommandInteraction`, Any], Any]
        the option's converter, takes in an interaction and the argument
    """

    TYPES: ClassVar[Dict[type, int]] = {
        str: 3,
        int: 4,
        bool: 5,
        disnake.abc.User: 6,
        disnake.User: 6,
        disnake.Member: 6,
        # channels handled separately
        disnake.abc.GuildChannel: 7,
        disnake.Role: 8,
        Union[disnake.Member, disnake.Role]: 9,
        disnake.abc.Snowflake: 9,
        float: 10,
    }

    def __init__(
        self,
        default: Any = ...,
        *,
        name: str = "",
        description: str = None,
        converter: Callable[[Interaction, Any], Any] = None,
        autcomplete: Callable[[Interaction, str], Any] = None,
        choices: Choices = None,
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

        self.le = _xt_to_xe(le, lt, -1)
        self.ge = _xt_to_xe(ge, gt, 1)

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

    def __repr__(self):
        return f"<Param default={self.default!r} name={self.name!r} description={self.description!r}>"

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

    def parse_annotation(self, annotation: Any) -> None:  # sourcery no-metrics
        # TODO: Clean up whatever the fuck this is
        if isinstance(annotation, ParamInfo):
            default = "..." if annotation.default is ... else repr(annotation.default)
            r = f'Param({default}, description={annotation.description or "description"!r})'
            raise TypeError(f'Param must be a parameter default, not an annotation: "option: type = {r}"')

        # Get rid of Optionals
        if get_origin(annotation) is Union:
            args = [i for i in annotation.__args__ if i not in (None, type(None))]
            if len(args) == 1:
                annotation = args[0]
            else:
                annotation.__args__ = args

        if self.converter is not None:
            # try to parse the converter's annotation, fall back on the annotation itself
            parameters = list(inspect.signature(self.converter).parameters.values())
            parameter = parameters[2] if inspect.ismethod(self.converter) else parameters[1]
            conv_annot = get_type_hints(self.converter).get(parameter.name, Any)

            if conv_annot in self.TYPES:
                self.type = conv_annot
                return
            elif isinstance(conv_annot, EnumMeta) or get_origin(conv_annot) is Literal:
                self._parse_enum(conv_annot)
                return
            elif conv_annot is not Any:
                raise TypeError("Converters cannot use converter annotations")
            elif annotation in CONVERTER_MAPPING:
                raise TypeError(
                    "Cannot use an implicit converter annotation and an unnanotated converter at the same time"
                )
            # otherwise just parse the annotation normally and hope for the best

        if annotation is inspect.Parameter.empty or annotation is Any:
            pass
        elif get_origin(annotation) is list:
            if self.converter:
                raise TypeError("Converter detected with custom annotation")
            arg = annotation.__args__[0] if annotation.__args__ else str
            if arg in [str, int, float]:
                conv = arg
            elif arg in CONVERTER_MAPPING:
                # TODO: Define our own converters?
                raise TypeError("Discord's api is not mature enough to handle member conversion with models")
            else:
                raise TypeError(f"{arg!r} is not a valid List subscript for Param")
            self.converter = lambda inter, arg: list(map(conv, arg.split()))
        elif isinstance(annotation, (EnumMeta, disnake.enums.EnumMeta)) or get_origin(annotation) is Literal:
            self._parse_enum(annotation)

        elif get_origin(annotation) is Union:
            args = annotation.__args__
            if all(issubclass(channel, disnake.abc.GuildChannel) for channel in args):
                self.type = disnake.abc.GuildChannel
                channel_types = set()
                for channel in args:
                    channel_types.union(_channel_type_factory(channel))
                self.channel_types = list(channel_types)
            elif annotation in self.TYPES:
                self.type = annotation
            elif any(get_origin(arg) for arg in args):
                raise TypeError("Unions do not support nesting")
            else:
                raise TypeError("Unions for anything else other than channels are not supported")
        elif isinstance(annotation, type) and issubclass(annotation, disnake.abc.GuildChannel):
            self.type = disnake.abc.GuildChannel
            self.channel_types = _channel_type_factory(annotation)

        elif annotation in self.TYPES:
            self.type = annotation
        elif annotation in CONVERTER_MAPPING:
            self.converter = CONVERTER_MAPPING[annotation]().convert
        else:
            raise TypeError(f"{annotation!r} is not a valid Param annotation")

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
            min_value=self.ge,
            max_value=self.le,
        )


def expand_params(command: AnySlashCommand) -> List[Option]:
    """Update an option with its params *in-place*

    Returns the created options
    """
    # parse annotations:
    sig = inspect.signature(command.callback)
    parameters = list(sig.parameters.values())

    # hacky I suppose
    cog = parameters[0].name == "self" if command.cog is None else True
    inter_param = parameters[1] if cog else parameters[0]
    parameters = parameters[2:] if cog else parameters[1:]
    type_hints = get_type_hints(command.callback)

    # extract params:
    params = []
    for parameter in parameters:
        if parameter.kind in [inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD]:
            continue
        param = parameter.default
        if not isinstance(param, ParamInfo):
            param = ParamInfo(param if param is not parameter.empty else ...)

        doc_param = command.docstring["params"].get(parameter.name)

        param.parse_parameter(parameter)
        if doc_param:
            param.parse_doc(doc_param["type"], doc_param["description"])
        param.parse_annotation(type_hints.get(parameter.name, Any))
        params.append(param)

    # update connectors and autocompleters
    for param in params:
        if param.name != param.param_name:
            command.connectors[param.name] = param.param_name
        if param.autocomplete:
            command.autocompleters[param.name] = param.autocomplete

    # add custom decorators
    inter_annot = type_hints.get(inter_param.name, Any)
    if isinstance(inter_annot, type) and issubclass(inter_annot, disnake.GuildCommandInteraction):
        command.guild_only = True

    return [param.to_option() for param in params]


async def resolve_param_kwargs(func: Callable, inter: Interaction, kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Resolves a call with kwargs and transforms into normal kwargs

    Depends on the fact that optionparams already contain all info.
    """
    sig = inspect.signature(func)

    for parameter in sig.parameters.values():
        if parameter.kind in [inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD]:
            continue
        param = parameter.default
        if not isinstance(param, ParamInfo):
            continue

        if param.param_name in kwargs:
            kwargs[param.param_name] = await param.convert_argument(inter, kwargs[param.param_name])
        else:
            kwargs[param.param_name] = await param.get_default(inter)

    return kwargs


@overload
def Param(
    default: Any = ...,
    *,
    name: str = "",
    desc: str = None,
    choices: Choices = None,
    conv: Callable[[Interaction, Any], Any] = None,
    autocomp: Callable[[Interaction, str], Any] = None,
    ge: float = None,
    le: float = None,
) -> Any:
    ...


@overload
def Param(
    default: Any = ...,
    *,
    name: str = "",
    desc: str = None,
    choices: Choices = None,
    conv: Callable[[Interaction, Any], Any] = None,
    autocomp: Callable[[Interaction, str], Any] = None,
    gt: float = None,
    lt: float = None,
) -> Any:
    ...


@overload
def Param(
    default: Any = ...,
    *,
    name: str = "",
    description: str = None,
    choices: Choices = None,
    converter: Callable[[Interaction, Any], Any] = None,
    autocomplete: Callable[[Interaction, str], Any] = None,
    min_value: float = None,
    max_value: float = None,
) -> Any:
    ...


def Param(
    default: Any = ...,
    *,
    name: str = "",
    desc: str = None,
    description: str = None,
    choices: Choices = None,
    conv: Callable[[Interaction, Any], Any] = None,
    converter: Callable[[Interaction, Any], Any] = None,
    autocomp: Callable[[Interaction, str], Any] = None,
    autocomplete: Callable[[Interaction, str], Any] = None,
    lt: float = None,
    le: float = None,
    gt: float = None,
    ge: float = None,
    min_value: float = None,
    max_value: float = None,
) -> Any:
    return ParamInfo(
        default,
        name=name,
        description=desc or description,
        choices=choices,
        converter=conv or converter,
        autcomplete=autocomp or autocomplete,
        lt=lt,
        le=le if max_value is None else max_value,
        gt=gt,
        ge=ge if min_value is None else min_value,
    )


param = Param


def option_enum(choices: Union[Dict[str, TChoice], List[TChoice]], **kwargs: TChoice) -> Type[TChoice]:
    if isinstance(choices, list):
        # invariance issue, please fix
        choices = cast(Dict[str, TChoice], {str(i): i for i in choices})

    choices = choices or kwargs
    first, *_ = choices.values()
    return Enum("", choices, type=type(first))
