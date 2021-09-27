.. currentmodule:: disnake

.. _ext_commands_slash_commands:

Slash Commands
==============

Slash commands can significantly simplify the user's experience with your bot. Once "/" is pressed on the keyboard,
the list of slash commands appears. You can fill the options and read the hints at the same time, while types are validated
instantly. This library allows to make such commands in several minutes, regardless of their complexity.

For example, here's a simple slash command:

.. code-block:: python3

    @bot.slash_command(description="Responds with 'World'")
    async def hello(inter):
        await inter.response.send_message("World")

A slash command must always have at least one parameter, ``inter``, which is the :class:`.ApplicationCommandInteraction` as the first one.

Before this command is visible in discord, it should be registered. By default, registration is global, it takes up to 1 hour.
If you want this process to be faster during development, set ``test_guilds`` kwarg of ``commands.Bot`` to the list of IDs of your test guilds,
like so: ``bot = commands.Bot(..., test_guilds=[123456789])``

.. _param_syntax:

Parameters
----------

This library is using a fastapi-like syntax for defining the slash command options.

Here's an example of a command with one integer option:

.. code-block:: python3

    @bot.slash_command(description="Multiplies the number by 7")
    async def multiply(inter, number: int):
        await inter.response.send_message(number * 7)

[Not finished]
