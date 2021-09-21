"""Repsonsible for handling Params for slash commands"""
from __future__ import annotations

import inspect
from enum import Enum, EnumMeta
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Literal, Type, TypeVar, Union, get_origin, get_type_hints

import disnake
from disnake.app_commands import Option, OptionChoice
from disnake.enums import OptionType, try_enum_to_int

if TYPE_CHECKING:
    from disnake.interactions import ApplicationCommandInteraction as Interaction

TChoice = TypeVar("TChoice", str, int)

__all__ = (
    "extract_params",
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

    TYPES: Dict[type, int] = {
        str: 3,
        int: 4,
        bool: 5,
        disnake.abc.User: 6,
        disnake.User: 6,
        disnake.Member: 6,
        disnake.abc.GuildChannel: 7,
        disnake.TextChannel: 7,
        disnake.VoiceChannel: 7,
        disnake.CategoryChannel: 7,
        disnake.StageChannel: 7,
        disnake.StoreChannel: 7,
        disnake.Role: 8,
        Union[disnake.Member, disnake.Role]: 9,
        disnake.abc.Snowflake: 9,
        float: 10,
    }

    def __init__(
        self,
        default: Any = ...,
        *,
        name: str = '',
        description: str = None,
        converter: Callable[[Interaction, Any], Any] = None,
        choices: List[OptionChoice] = None,
        type: type = str,
    ) -> None:
        self.default = default
        self.name = name
        self.param_name = name
        self.description = description or "\u200b"
        self.converter = converter

        self.choices = choices or []
        self.type = type

    @property
    def required(self):
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

    async def convert_argument(self, inter: Interaction, argument: Any) -> Any:
        """Convert a value if a converter is given"""
        if self.converter is None:
            return argument
        
        argument = self.converter(inter, argument)
        if inspect.isawaitable(argument):
            return await argument
        
        return argument
        

    def parse_annotation(self, annotation: Any) -> None:
        if annotation is inspect.Parameter.empty or annotation is Any:
            pass
        elif isinstance(annotation, EnumMeta):
            self.choices = [OptionChoice(name, value) for name, value in annotation.__members__.items()]  # type: ignore
            self.type = type(self.choices[0].value)
        elif get_origin(annotation) is Literal:
            self.choices = [OptionChoice(str(i), i) for i in annotation.__args__]
            self.type = type(self.choices[0].value)
        elif annotation in self.TYPES:
            self.type = annotation
        else:
            raise TypeError(f"{annotation!r} is not a valid Param annotation")

    def parse_parameter(self, param: inspect.Parameter) -> None:
        self.name = self.name or param.name.replace("_", "-")
        self.param_name = param.name

    def to_option(self) -> Option:
        if self.name == '':
            raise TypeError("Param must be parsed first")

        return Option(
            name=self.name,
            description=self.description,
            type=self.discord_type,
            required=self.required,
            choices=self.choices,
        )


def extract_params(func: Callable, cog: Any = None) -> List[Param]:
    """Extract params from a function signature"""
    sig = inspect.signature(func)
    parameters = list(sig.parameters.values())
    if cog is None:
        # hacky I suppose
        cog = parameters[0].name == 'self'
    parameters = parameters[2:] if cog else parameters[1:]
    type_hints = get_type_hints(func)

    params = []
    for parameter in parameters:
        if parameter.kind in [inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD]:
            continue
        param = parameter.default
        if not isinstance(param, Param):
            param = Param(param if param is not parameter.empty else ...)

        param.parse_parameter(parameter)
        param.parse_annotation(type_hints.get(parameter.name, Any))
        params.append(param)

    return params


def create_connector(params: List[Param]) -> Dict[str, Any]:
    """Create a connector for each param"""
    return {
        param.name: param.param_name
        for param in params
        if param.name != param.param_name
    }


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

def param(
    default: Any = ...,
    *,
    name: str = '',
    desc: str = None,
    description: str = None,
    conv: Callable[[Interaction, Any], Any] = None,
    converter: Callable[[Interaction, Any], Any] = None,
    choices: List[OptionChoice] = None,
) -> Any:
    return Param(default, name=name, description=desc or description, converter=conv or converter, choices=choices)


def option_enum(choices: Union[Dict[str, TChoice], List[TChoice]], **kwargs: TChoice) -> Type[TChoice]:
    if isinstance(choices, list):
        choices = {str(i): i for i in choices}

    choices = choices or kwargs
    first, *_ = choices.values()
    return Enum("", choices, type=type(first))
