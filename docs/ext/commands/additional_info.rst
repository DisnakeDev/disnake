.. currentmodule:: disnake

.. _ext_commands_additional_info:

Additional info
===============

This section contains explanations of some library mechanics which may be useful to know.

.. _app_command_sync:

App command sync
----------------

If you're using :ref:`discord_ext_commands` for application commands (slash commands, context menus) you should
understand how your commands show up in Discord. If ``sync_commands`` kwarg of :class:`Bot <ext.commands.Bot>` (or a similar class) is set to ``True`` (which is the default value)
the library registers / updates all commands automatically. Based on the application commands defined in your code it decides
which commands should be registered, edited or deleted but there're some edge cases you should keep in mind.

Changing test guilds
++++++++++++++++++++

If you remove some IDs from the ``test_guilds`` kwarg of :class:`Bot <ext.commands.Bot>` (or a similar class) or from the ``guild_ids`` kwarg of
:func:`slash_command <ext.commands.slash_command>` (:func:`user_command <ext.commands.user_command>`, :func:`message_command <ext.commands.message_command>`)
the commands in those guilds won't be deleted instantly. Instead, they'll be deleted as soon as one of the deprecated commands is invoked. Your bot will send a message
like "This command has just been synced ...".

Hosting the bot on multiple machines
++++++++++++++++++++++++++++++++++++

If your bot requires shard distribution across several machines, you should set ``sync_commands`` kwarg to ``False`` everywhere except 1 machine.
This will prevent conflicts and race conditions. Discord API doesn't provide users with events related to application command updates,
so it's impossible to keep the cache of multiple machines synced. Having only 1 machine with ``sync_commands`` set to ``True`` is enough
because global registration of application commands doesn't depend on sharding.

.. _why_params_and_injections_return_any:

Why do ``Param`` and ``Injection``-related functions return ``Any``?
--------------------------------------------------------------------

If your editor of choice supports type-checking, you may have noticed that :func:`~ext.commands.Param`, :func:`~ext.commands.inject`,
and :func:`~ext.commands.injection` do not have a specific return type, but at runtime these return :class:`~ext.commands.ParamInfo` and
:class:`~ext.commands.Injection` respectively.

A typical example of a slash command might look like this: ::

    @bot.slash_command(description="Replies with the given text!")
    async def echo(
        inter: disnake.ApplicationCommandInteraction,
        text: str = commands.Param(description="Echo~")
    ) -> None:
        await inter.response.send_message(text)

Here, you have two parameters in your command's function: ``inter``, an instance of :class:`disnake.ApplicationCommandInteraction`, and
``text``, which is somewhat unusual: you annotate ``text`` as ``str``, but at the same time, assign a :class:`~ext.commands.ParamInfo` instance to it.
That's the thing. When your editor type-checks your (any library's) code, it would normally complain if you tried to do the above, because
you're trying to "convert" ``ParamInfo`` into ``str``, but since library have set ``Param``'s return type as ``Any``, type-checker "accepts"
your code, because ``str`` (and any type) is the subset of ``Any``. Win-win!

The same thing applies to :func:`~ext.commands.inject`, :func:`~ext.commands.injection` and :func:`~ext.commands.register_injection`.
