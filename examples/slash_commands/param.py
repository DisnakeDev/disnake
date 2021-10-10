import disnake
from disnake.ext import commands
from disnake.ext.commands import Param as Parameter


bot = commands.Bot("!")


# Disnake can use a fastapi-like option syntax.
# That means instead of using the options keyword you will be
# setting the default of your parameters.
# It should allow you to create more readable commands and make the more complicated
# features easier to use.
# Not only that but using Parameter even adds support for a ton of other features.

# We create a new command with two options: "required" (a required string) and "optional" (an integer).
# Parameter takes care of parsing the annotation and adding a description for it.
# If you want to provide a default value and make the option optional simply provide it as the first argument.
# "description" may be shortened to "desc" if you so choose.
@bot.slash_command(name="simple-command", description="Some Simple command")
async def simple(
    inter: disnake.ApplicationCommandInteraction,
    required: str = Parameter(desc="The required argument"),
    optional: int = Parameter(description="The optional argument", default=0),
) -> None:
    ...  # There should be a code here:3


# To make an option required don't provide a default or set it to "..."
# Callable defaults are allowed too, in this case it defaults to the author.
@bot.slash_command()
async def defaults(
    inter: disnake.ApplicationCommandInteraction,
    required: str = Parameter(description="a"),
    also_required: str = Parameter(..., description="b"),
    member: str = Parameter(default=lambda inter: inter.author),
) -> None:
    ...


# Names are automatically discerned from the parameter name
# However you may want to provide your own name in some cases.
@bot.slash_command()
async def names(
    inter: disnake.ApplicationCommandInteraction,
    class_: str = Parameter(name="class", description="Your class")
) -> None:
    ...


# Commands may be limited only to guilds with a special interaction annotation
@bot.slash_command()
async def guild_command(
    inter: disnake.GuildCommandInteraction
) -> None:
    ...


# Not all types are currently supported by discord, you may use converters in these cases.
# Both old command converters using annotations and converters using functions are supported.
# However converters which are not consistent with the actual type are not allowed.
# That means no Converter classes and no fuckery like clean_content may be used in an annotation.
@bot.slash_command()
async def converters(
    inter: disnake.ApplicationCommandInteraction,
    emoji: disnake.Emoji = Parameter(description="An emoji"),
    content: str = Parameter(description="Clean content", converter=lambda inter, arg: arg.replace("@", r"\@")),
) -> None:
    ...


# Converters may also dictate the type of the option
# (In case no annotation is present the code falls back to the normal annotation)
def get_username(inter, user: disnake.User) -> str:
    return user.name + '#' + user.discriminator  # str(user) is better here but shhhh


@bot.slash_command()
async def advanced_converters(
    inter: disnake.ApplicationCommandInteraction,
    username: str = Parameter(name="user", description="A user", converter=get_username)
) -> None:
    ...


# Lists are kind of supported too, it simply splits all arguments by space
from typing import List  # Do not import at the module level not at the top of the file, this is done on purpose!!!


@bot.slash_command()
async def list_converters(
    inter: disnake.ApplicationCommandInteraction,
    numbers: List[int] = Parameter(description="A list of numbers")
) -> None:
    ...

# Enumeration (choices) is allowed using enum.Enum, commands.option_enum or Literal
# The user will see the enum member name or the dict key and the bot will receive the value.
from enum import Enum
from typing import Literal


class Color(int, Enum):
    red = 0xe74c3c
    green = 0x2ecc71
    blue = 0x3498db
    yellow = 0xfee75c


Gender = commands.option_enum(["Male", "Female", "Other", "Prefer Not To Say"])
Language = commands.option_enum({"English": "en", "French": "fr", "Spanish": "es"})


@bot.slash_command()
async def enumeration(
    inter: disnake.ApplicationCommandInteraction,
    color: Color = Parameter(description="Your favorite color"),
    gender: Gender = Parameter(description="Your gender"),
    language: Language = Parameter(description="Your language"),
    mode: Literal[1, 2, 3] = Parameter(description="Mode of your choosing"),
) -> None:
    ...


# Specific channel types may be specified.
# To specify multiple channel types use either abcs or unions.
from typing import Union


@bot.slash_command()
async def constraint(
    inter: disnake.ApplicationCommandInteraction,
    text: disnake.TextChannel = Parameter(description="A text channel"),
    voice: disnake.VoiceChannel = Parameter(description="A voice channel"),
    fancy: Union[disnake.NewsChannel, disnake.StoreChannel] = Parameter(description="A fancy new channel"),
    any: disnake.abc.GuildChannel = Parameter(description="Any channel you can imagine")
) -> None:
    ...


# You may even add autocompletion for your commands.
# This requires the type to be a string and for you to not use enumeration.
# Your autocompleter may return either a dict of names to values or a list of names
# but the amount of options cannot be more than 20.

LANGUAGES = ["Python", "JavaScript", "TypeScript", "Java", "Rust", "Lisp", "Elixir"]


async def autocomplete_langs(inter: disnake.ApplicationCommandInteraction, string: str) -> List[str]:
    return list(filter(lambda lang: string in lang.lower(), LANGUAGES))


@bot.slash_command()
async def autocomplete(
    inter: disnake.ApplicationCommandInteraction,
    language: str = Parameter(description="Your favorite language", autocomplete=autocomplete_langs)
) -> None:
    ...


# You can use docstrings to set the description of the command or even
# the description of options. You should follow the ReStructuredText or numpy format.
@bot.slash_command()
async def docstrings(
    inter: disnake.ApplicationCommandInteraction,
    user: disnake.User,
    reason: str,
) -> None:
    """
    This command shows how docstrings are being parsed.

    Parameters
    ----------
    user: :class:`disnake.User`
        Enter the user
    reason: :class:`str`
        Enter the reason
    """
    ...


# Types of parameters in docstrings are optional.
# You can specify the descriptions without them.
@bot.slash_command()
async def partial_docstrings(
    inter: disnake.ApplicationCommandInteraction,
    user: disnake.User,
    reason: str,
) -> None:
    """
    This command shows how docstrings are being parsed.

    Parameters
    ----------
    user
        Enter the user
    reason
        Enter the reason
    """
    ...


# If you don't want to waste too many lines
# use ':' to separate the param name and description.
@bot.slash_command()
async def simple_docstrings(
    inter: disnake.ApplicationCommandInteraction,
    user: disnake.User,
    reason: str,
) -> None:
    """
    This command shows how docstrings are being parsed.

    Parameters
    ----------
    user: Enter the user
    reason: Enter the reason
    """
    ...
