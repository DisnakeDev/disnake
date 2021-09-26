"""Repsonsible for handling Params for slash commands"""
from __future__ import annotations

import inspect
from enum import Enum, EnumMeta
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    List,
    Literal,
    Type,
    TypeVar,
    Union,
    get_origin,
    get_type_hints,
    overload,
)

import disnake
from disnake.app_commands import Option, OptionChoice
from disnake.channel import _channel_type_factory
from disnake.enums import ChannelType, OptionType, try_enum_to_int

from . import errors
from .converter import CONVERTER_MAPPING

if TYPE_CHECKING:
    from disnake.interactions import ApplicationCommandInteraction as Interaction

TChoice = TypeVar("TChoice", str, int)

__all__ = (
    "param",
    "option_enum",
)


class Param:
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
    choices: List[:class:`OptionChoice`]
    type: :class:`type`
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
        choices: List[OptionChoice] = None,
        type: type = str,
        channel_types: List[ChannelType] = None,
    ) -> None:
        self.default = default
        self.name = name
        self.param_name = name
        self.description = description
        self.converter = converter
        self.autocomplete = autcomplete

        self.choices = choices or []
        self.type = type
        self.channel_types = channel_types or []

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

    def parse_annotation(self, annotation: Any) -> None:
        if isinstance(annotation, Param):
            default = "..." if annotation.required else repr(annotation.default)
            r = f'Param({default}, description={annotation.description or "description"!r})'
            raise TypeError(f"Param must be a parameter default, not an annotation: \"option: type = {r}\"")
        
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
            elif conv_annot is not Any:
                # TODO: Implement at least enum for converters
                raise TypeError("Converters cannot use converter annotations")
            elif annotation in CONVERTER_MAPPING:
                raise TypeError(
                    "Cannot use an implicit converter annotation and an unnanotated converter at the same time"
                )
            # otherwise just parse the annotation normally and hope for the best

        if annotation is inspect.Parameter.empty or annotation is Any:
            pass
        elif isinstance(annotation, EnumMeta):
            self.choices = [OptionChoice(name, value) for name, value in annotation.__members__.items()]  # type: ignore
            self.type = type(self.choices[0].value)
        elif get_origin(annotation) is Literal:
            self.choices = [OptionChoice(str(i), i) for i in annotation.__args__]
            self.type = type(self.choices[0].value)

        elif get_origin(annotation) is Union:
            args = annotation.__args__
            if all(issubclass(channel, disnake.abc.GuildChannel) for channel in args):
                self.type = disnake.abc.GuildChannel
                self.channel_types = []
                for channel in args:
                    self.channel_types += _channel_type_factory(channel)
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
        self.name = self.name or param.name.replace("_", "-")
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
        )


def extract_params(func: Callable, cog: Any = None, doc_params: Dict[str, Dict[str, Any]] = {}) -> List[Param]:
    """Extract params from a function signature"""
    sig = inspect.signature(func)
    parameters = list(sig.parameters.values())
    if cog is None:
        # hacky I suppose
        cog = parameters[0].name == "self"
    parameters = parameters[2:] if cog else parameters[1:]
    type_hints = get_type_hints(func)

    params = []
    for parameter in parameters:
        if parameter.kind in [inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD]:
            continue
        param = parameter.default
        if not isinstance(param, Param):
            param = Param(param if param is not parameter.empty else ...)

        doc_param = doc_params.get(parameter.name)

        param.parse_parameter(parameter)
        if doc_param:
            param.parse_doc(doc_param["type"], doc_param["description"])
        param.parse_annotation(type_hints.get(parameter.name, Any))
        params.append(param)

    return params


def create_connectors(params: List[Param]) -> Dict[str, Any]:
    """Create a connector for each param"""
    return {param.name: param.param_name for param in params if param.name != param.param_name}


def create_autocompleters(params: List[Param]) -> Dict[str, Callable[[Interaction, str], Any]]:
    """Create an autocomplete for each param"""
    return {param.name: param.autocomplete for param in params if param.autocomplete}


async def resolve_param_kwargs(func: Callable, inter: Interaction, kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Resolves a call with kwargs and transforms into normal kwargs

    Depends on the fact that optionparams already contain all info.
    """
    sig = inspect.signature(func)

    for parameter in sig.parameters.values():
        if parameter.kind in [inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD]:
            continue
        param = parameter.default
        if not isinstance(param, Param):
            continue

        if param.param_name in kwargs:
            kwargs[param.param_name] = await param.convert_argument(inter, kwargs[param.param_name])
        else:
            kwargs[param.param_name] = await param.get_default(inter)

    return kwargs


@overload
def param(
    default: Any = ...,
    *,
    name: str = "",
    desc: str = None,
    conv: Callable[[Interaction, Any], Any] = None,
    autocomp: Callable[[Interaction, str], Any] = None,
    choices: List[OptionChoice] = None,
) -> Any:
    ...


@overload
def param(
    default: Any = ...,
    *,
    name: str = "",
    description: str = None,
    converter: Callable[[Interaction, Any], Any] = None,
    autocomplete: Callable[[Interaction, str], Any] = None,
    choices: List[OptionChoice] = None,
) -> Any:
    ...


def param(
    default: Any = ...,
    *,
    name: str = "",
    desc: str = None,
    description: str = None,
    conv: Callable[[Interaction, Any], Any] = None,
    converter: Callable[[Interaction, Any], Any] = None,
    autocomp: Callable[[Interaction, str], Any] = None,
    autocomplete: Callable[[Interaction, str], Any] = None,
    choices: List[OptionChoice] = None,
) -> Any:
    return Param(
        default,
        name=name,
        description=desc or description,
        converter=conv or converter,
        choices=choices,
        autcomplete=autocomp or autocomplete,
    )


def option_enum(choices: Union[Dict[str, TChoice], List[TChoice]], **kwargs: TChoice) -> Type[TChoice]:
    if isinstance(choices, list):
        choices = {str(i): i for i in choices}

    choices = choices or kwargs
    first, *_ = choices.values()
    return Enum("", choices, type=type(first))
