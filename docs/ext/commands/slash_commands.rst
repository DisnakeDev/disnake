.. currentmodule:: disnake

.. _ext_commands_slash_commands:

Slash Commands
==============

Slash commands can significantly simplify the user's experience with your bot. Once "/" is pressed on the keyboard,
the list of slash commands appears. You can fill the options and read the hints at the same time, while types are validated
instantly. This library allows to make such commands in several minutes, regardless of their complexity.

.. _slash_commands_start:

Getting started
---------------

You have probably noticed that slash commands have really interactive user interface, as if each slash command was built-in.
This is because each slash command is registered in Discord before people can see it. This library handles registration for you,
but you can still manage it.

By default, the registration is global. This means that your slash commands will be visible everywhere, including bot DMs.
Global registration can take up to 1 hour to complete, this is an API limitation. You can change the registration to be local,
so your slash commands will only be visible in several guilds. This type of registration is almost instant.

This code sample shows how to set the registration to be local:

.. code-block:: python3

    from disnake.ext import commands

    bot = commands.Bot(
        command_prefix='!',
        test_guilds=[123456789],
        # In the list above you can specify the IDs of your test guilds.
        # Why is this kwarg called test_guilds? This is because you're not meant to use
        # local registration in production, since you may exceed the rate limits.
    )

For global registration, don't specify this parameter.

Another useful parameter is ``sync_commands_debug``. If set to ``True``, you receive debug messages related to the
app command registration. This is useful if you want to figure out some registration details:

.. code-block:: python3

    from disnake.ext import commands

    bot = commands.Bot(
        command_prefix='!',
        test_guilds=[123456789], # Optional
        sync_commands_debug=True
    )

If you want to disable the automatic registration, set ``sync_commands`` to ``False``:

.. code-block:: python3

    from disnake.ext import commands

    bot = commands.Bot(
        command_prefix='!',
        sync_commands=False
    )

Basic Slash Command
-------------------

Make sure that you've read :ref:`slash_commands_start`, it contains important information about command registration.

Here's an example of a slash command:

.. code-block:: python3

    @bot.slash_command(description="Responds with 'World'")
    async def hello(inter):
        await inter.response.send_message("World")

A slash command must always have at least one parameter, ``inter``, which is the :class:`.ApplicationCommandInteraction` as the first one.

I can't see my slash command, what do I do? Read :ref:`slash_commands_start`.

.. _param_syntax:

Parameters
----------

You may want to define a couple of options for your slash command. In disnake, the definition of options is based on annotations.

Here's an example of a command with one integer option (without a description):

.. code-block:: python3

    @bot.slash_command(description="Multiplies the number by 7")
    async def multiply(inter, number: int):
        await inter.response.send_message(number * 7)

The result should look like this:

.. image:: /images/app_commands/int_option.png

[Not finished]
