[![Disnake Banner](https://raw.githubusercontent.com/DisnakeDev/disnake/master/assets/banner.png)](https://disnake.dev/)

<div align="center">
<h1>disnake</h1>
<p>
    <a href="https://discord.gg/disnake"><img src="https://img.shields.io/discord/808030843078836254?style=flat-square&color=5865f2&logo=discord&logoColor=ffffff&label=discord" alt="Discord server invite" /></a>
    <a href="https://pypi.python.org/pypi/disnake"><img src="https://img.shields.io/pypi/v/disnake.svg?style=flat-square" alt="PyPI version info" /></a>
    <a href="https://pypi.python.org/pypi/disnake"><img src="https://img.shields.io/pypi/pyversions/disnake.svg?style=flat-square" alt="PyPI supported Python versions" /></a>
    <a href="https://github.com/DisnakeDev/disnake/commits"><img src="https://img.shields.io/github/commit-activity/w/DisnakeDev/disnake.svg?style=flat-square" alt="Commit activity" /></a></p>

A modern, easy to use, feature-rich, and async ready API wrapper for Discord written in Python.
  
Key Features
------------

-> Proper rate limit handling.<br>
-> Type-safety measures.<br>
-> [FastAPI](https://fastapi.tiangolo.com/) - like slash command syntax.<br>
<br>
<sup>The syntax and structure of `discord.py 2.0` is preserved.</sup>

<h1>Installing</h1>


**Python 3.8 or higher is required.**

To install the library without full voice support, you can just run the
following command:
    
</div>

``` sh
# Linux/macOS
python3 -m pip install -U disnake

# Windows
py -3 -m pip install -U disnake
```

<div align="center">
<br>
    
Installing `disnake` with full voice support requires you to replace `disnake` here, with `disnake[voice]`. To learn more about voice support (or installing the development version), please visit [this section of our guide](https://guide.disnake.dev/prerequisites/installing-disnake/).

(You can optionally install [PyNaCl](https://pypi.org/project/PyNaCl/) for voice support.)

Note that voice support on Linux requires installation of `libffi-dev` and `python-dev` packages, via your preferred package manager (e.g. `apt`, `dnf`, etc.) before running the following commands.

<br>
    
Versioning
----------

This project does **not** quite follow semantic versioning; for more details, see [version guarantees](https://docs.disnake.dev/en/latest/version_guarantees.html).

To be on the safe side and avoid unexpected breaking changes, pin the dependency to a minor version (e.g. `disnake==a.b.*` or `disnake~=a.b.c`) or an exact version (e.g. `disnake==a.b.c`).

<br>    
    
Quick Example
-------------

### Slash Commands Example
    
</div>

``` py
import disnake
from disnake.ext import commands

bot = commands.InteractionBot(test_guilds=[12345])

@bot.slash_command()
async def ping(inter):
    await inter.response.send_message("Pong!")

bot.run("BOT_TOKEN")
```

<div align="center">
    
### Context Menus Example
</div>

``` py
import disnake
from disnake.ext import commands

bot = commands.InteractionBot(test_guilds=[12345])

@bot.user_command()
async def avatar(inter, user):
    embed = disnake.Embed(title=str(user))
    embed.set_image(url=user.display_avatar.url)
    await inter.response.send_message(embed=embed)

bot.run("BOT_TOKEN")
```
<div align="center">
    
### Prefix Commands Example
</div>

``` py
import disnake
from disnake.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned)

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

bot.run("BOT_TOKEN")
```

<div align="center">
<br><br>
    
You can find more examples in the [examples directory](./examples).
    
<br>
<br>
<p align="center">
    <a href="https://docs.disnake.dev/">Documentation</a>
    ⁕
    <a href="https://guide.disnake.dev/">Guide</a>
    ⁕
    <a href="https://discord.gg/disnake">Discord Server</a>
    ⁕
    <a href="https://discord.gg/discord-developers">Discord Developers</a>
</p>
<br>
</div>
